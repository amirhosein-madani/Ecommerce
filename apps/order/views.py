import logging
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView

from accounts.mixins import LoginRequiredMixin
from cart.models import Cart
from dashboard.permissions import HasCustomerAccessPermission
from order.forms import CheckOutForm
from order.models.coupons import Coupon, CouponUsage
from order.models.orders import (
    Order,
    OrderItem,
    OrderStatusType,
    UserAddress,
)
from order.services import (
    CouponNotApplicable,
    InsufficientStock,
    validate_and_apply_coupon,
)
from payment.models import Payment, PaymentStatus
from payment.zarinpal_client import ZarinPal
from products.models import Product

logger = logging.getLogger(__name__)

TAX_RATE = Decimal("9") / Decimal("100")
TWO_PLACES = Decimal("0.01")


def calculate_totals(total_price: Decimal, tax_rate: Decimal = TAX_RATE):
    """Return (total_price, tax) both rounded to 2 decimal places."""
    tax = (total_price * tax_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    return total_price, tax


def lock_and_check_stock(cart_items):
    """
    Lock the relevant Product rows (in a stable order to avoid deadlocks),
    validate stock, and return a {product_id: product} map of locked rows.

    Must be called inside a transaction.atomic() block.
    Raises InsufficientStock if any item exceeds available stock.
    """
    product_ids = sorted({item.product_id for item in cart_items})

    locked_products = {
        product.pk: product
        for product in Product.objects.select_for_update().filter(pk__in=product_ids)
    }

    for item in cart_items:
        product = locked_products[item.product_id]
        if item.quantity > product.stock:
            raise InsufficientStock(product.title)

    return locked_products


def decrease_stock(locked_products, cart_items):
    """Decrease stock for each item. Products must already be locked."""
    for item in cart_items:
        product = locked_products[item.product_id]
        product.stock -= item.quantity
        product.save(update_fields=["stock"])


def restore_stock(order):
    """Restore stock for all items of an order (e.g. on cancellation/failure)."""
    with transaction.atomic():
        for item in order.items.select_related("product").all():
            product = Product.objects.select_for_update().get(pk=item.product_id)
            product.stock += item.quantity
            product.save(update_fields=["stock"])


class ValidateCouponView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    View,
):
    def post(self, request):
        code = request.POST.get("code", "").strip()

        coupon = Coupon.objects.filter(
            code=code,
            is_active=True,
        ).first()

        if not coupon:
            return JsonResponse(
                {"message": "کد تخفیف معتبر نیست."},
                status=400,
            )

        cart = get_object_or_404(
            Cart,
            user=request.user,
        )

        cart_items = cart.items.select_related("product").all()

        try:
            _, discount_amount = validate_and_apply_coupon(
                request.user,
                coupon,
                cart_items,
            )

        except CouponNotApplicable as e:
            return JsonResponse(
                {"message": str(e)},
                status=400,
            )

        total_price, total_tax = calculate_totals(cart.total_price - discount_amount)

        request.session["applied_coupon_code"] = coupon.code

        return JsonResponse(
            {
                "message": (f"کد تخفیف با موفقیت اعمال شد " f"({coupon.discount}%)"),
                "total_price": total_price,
                "total_tax": total_tax,
            }
        )


class CheckOutView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    FormView,
):
    template_name = "order/checkout.html"
    form_class = CheckOutForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_coupon(self):
        code = self.request.session.get("applied_coupon_code")

        if not code:
            return None

        return Coupon.objects.filter(
            code=code,
            is_active=True,
        ).first()

    def form_valid(self, form):

        # -----------------------------
        # Address
        # -----------------------------

        address = get_object_or_404(
            UserAddress,
            user=self.request.user,
            pk=form.cleaned_data["address_id"],
        )

        # -----------------------------
        # Cart
        # -----------------------------

        cart = get_object_or_404(
            Cart,
            user=self.request.user,
        )

        cart_items = list(cart.items.select_related("product").all())

        if not cart_items:
            messages.warning(
                self.request,
                "سبد خرید شما خالی است.",
            )

            return self.form_invalid(form)

        # -----------------------------
        # Coupon
        # -----------------------------

        coupon = self.get_coupon()

        try:
            discount_amount = Decimal("0")

            if coupon:
                _, discount_amount = validate_and_apply_coupon(
                    self.request.user,
                    coupon,
                    cart_items,
                )

            total_price, total_tax = calculate_totals(
                cart.total_price - discount_amount
            )

            payable_amount = total_price + total_tax

            # -----------------------------
            # Database Transaction
            # -----------------------------

            with transaction.atomic():

                # -----------------------------
                # Lock Stock, Validate & Reserve
                # (locking in a stable pk order avoids deadlocks between
                # concurrent checkouts that share products)
                # -----------------------------

                locked_products = lock_and_check_stock(cart_items)

                # -----------------------------
                # Create Order
                # -----------------------------

                order = Order.objects.create(
                    user=self.request.user,
                    shipping_address=address,
                    total_price=total_price,
                    tax_amount=total_tax,
                    coupon=coupon,
                    discount_amount=discount_amount,
                    status=OrderStatusType.PENDING,
                )

                # -----------------------------
                # Create Order Items
                # -----------------------------

                for item in cart_items:
                    product = locked_products[item.product_id]

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.final_price,
                    )

                decrease_stock(locked_products, cart_items)

                # -----------------------------
                # Create Payment
                # -----------------------------

                payment = Payment.objects.create(
                    order=order,
                    amount=payable_amount,
                    status=PaymentStatus.PENDING,
                )

        except CouponNotApplicable as e:

            messages.warning(
                self.request,
                str(e),
            )

            return self.form_invalid(form)

        except InsufficientStock as e:

            messages.warning(
                self.request,
                f"موجودی محصول «{e}» کافی نیست.",
            )

            return self.form_invalid(form)

        # -----------------------------
        # ZarinPal Request
        # -----------------------------

        zarinpal = ZarinPal()

        callback_url = self.request.build_absolute_uri(reverse("order:payment_verify"))

        try:

            authority = zarinpal.payment_request(
                amount=payment.amount,
                callback_url=callback_url,
                description=f"پرداخت سفارش #{order.id}",
                mobile=getattr(
                    self.request.user,
                    "mobile",
                    None,
                ),
                email=self.request.user.email,
            )

        except Exception as e:

            logger.exception(
                "ZarinPal payment request failed for order #%s",
                order.id,
            )

            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=["status"])

            order.status = OrderStatusType.CANCELED
            order.save(update_fields=["status"])

            restore_stock(order)

            messages.error(
                self.request,
                f"خطا در اتصال به درگاه پرداخت: {e}",
            )

            return redirect("order:checkout")

        # -----------------------------
        # Save Authority
        # -----------------------------

        payment.authority = authority

        payment.save(update_fields=["authority"])

        # Coupon session دیگر لازم نیست
        self.request.session.pop(
            "applied_coupon_code",
            None,
        )

        # -----------------------------
        # Redirect To ZarinPal
        # -----------------------------

        payment_url = zarinpal.generate_payment_url(authority)

        return redirect(payment_url)

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(**kwargs)

        cart = get_object_or_404(
            Cart,
            user=self.request.user,
        )

        total_price, total_tax = calculate_totals(cart.total_price)

        context["addresses"] = UserAddress.objects.filter(user=self.request.user)

        context["total_price"] = total_price

        context["total_tax"] = total_tax

        return context


class PaymentVerifyView(View):

    def get(self, request):

        # -----------------------------
        # Get ZarinPal Parameters
        # -----------------------------

        authority = request.GET.get("Authority")

        status = request.GET.get("Status")

        if not authority:
            return JsonResponse(
                {"message": ("Authority not found.")},
                status=400,
            )

        # -----------------------------
        # Find Payment
        # -----------------------------

        payment = get_object_or_404(
            Payment,
            authority=authority,
        )

        # -----------------------------
        # Already Paid
        # -----------------------------

        if payment.status == PaymentStatus.SUCCESS:
            return redirect("order:completed")

        # -----------------------------
        # User Canceled Payment
        # -----------------------------

        if status != "OK":

            payment.status = PaymentStatus.FAILED

            payment.save(update_fields=["status"])

            order = payment.order

            order.status = OrderStatusType.CANCELED

            order.save(update_fields=["status"])

            # Stock was reserved at checkout time; give it back now
            # that the user has explicitly canceled payment.
            restore_stock(order)

            return redirect("order:payment_failed")

        # -----------------------------
        # Verify Payment
        # -----------------------------

        zarinpal = ZarinPal()

        try:

            result = zarinpal.payment_verify(
                amount=payment.amount,
                authority=authority,
            )

        except Exception:

            logger.exception(
                "ZarinPal payment verify failed for payment #%s (authority=%s)",
                payment.pk,
                authority,
            )

            payment.status = PaymentStatus.FAILED

            payment.save(update_fields=["status"])

            order = payment.order

            order.status = OrderStatusType.CANCELED

            order.save(update_fields=["status"])

            restore_stock(order)

            return redirect("order:payment_failed")

        # -----------------------------
        # Get ZarinPal Code
        # -----------------------------

        code = result.get(
            "data",
            {},
        ).get("code")

        # -----------------------------
        # Payment Successful
        # -----------------------------

        if code in [100, 101]:

            with transaction.atomic():

                order = payment.order

                # -----------------------------
                # Lock Payment
                # -----------------------------

                payment = Payment.objects.select_for_update().get(pk=payment.pk)

                # -----------------------------
                # Prevent Duplicate Verify
                # -----------------------------

                if payment.status == PaymentStatus.SUCCESS:
                    return redirect("order:completed")

                # -----------------------------
                # Payment Success
                # Stock was already reserved (decreased) at checkout time,
                # so there is nothing to check or decrement here — we just
                # finalize the order and payment records.
                # -----------------------------

                payment.status = PaymentStatus.SUCCESS

                payment.ref_id = result["data"].get("ref_id")

                payment.save(
                    update_fields=[
                        "status",
                        "ref_id",
                    ]
                )

                order.status = OrderStatusType.PAID

                order.save(update_fields=["status"])

                # -----------------------------
                # Coupon Usage
                # IMPORTANT:
                # فقط بعد از پرداخت موفق
                # -----------------------------

                if order.coupon:

                    CouponUsage.objects.get_or_create(
                        user=order.user,
                        coupon=order.coupon,
                        defaults={
                            "order": order,
                        },
                    )

                # -----------------------------
                # Clear Cart
                # -----------------------------

                cart = Cart.objects.filter(user=order.user).first()

                if cart:

                    cart.items.all().delete()

            return redirect("order:completed")

        # -----------------------------
        # Payment Failed
        # -----------------------------

        payment.status = PaymentStatus.FAILED

        payment.save(update_fields=["status"])

        order = payment.order

        order.status = OrderStatusType.CANCELED

        order.save(update_fields=["status"])

        restore_stock(order)

        return redirect("order:payment_failed")


class PaymentFailedView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    TemplateView,
):
    template_name = "order/failed.html"


class OrderCompletedView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    TemplateView,
):
    template_name = "order/completed.html"
