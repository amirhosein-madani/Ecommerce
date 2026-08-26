from decimal import Decimal

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
from payment.models import Payment, PaymentStatus
from order.services import (
    CouponNotApplicable,
    InsufficientStock,
    validate_and_apply_coupon,
)
from payment.zarinpal_client import ZarinPal
from products.models import Product


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

        total_price = cart.total_price - discount_amount

        total_tax = total_price * Decimal("9") / Decimal("100")

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

        address = get_object_or_404(
            UserAddress,
            user=self.request.user,
            pk=form.cleaned_data["address_id"],
        )

        cart = get_object_or_404(
            Cart,
            user=self.request.user,
        )

        cart_items = cart.items.select_related("product").all()

        if not cart_items.exists():

            messages.warning(
                self.request,
                "سبد خرید شما خالی است.",
            )

            return self.form_invalid(form)

        coupon = self.get_coupon()

        try:

            discount_amount = Decimal("0")

            if coupon:
                _, discount_amount = validate_and_apply_coupon(
                    self.request.user,
                    coupon,
                    cart_items,
                )

            total_price = cart.total_price - discount_amount

            with transaction.atomic():

                # ----------------------
                # ایجاد Order
                # ----------------------

                order = Order.objects.create(
                    user=self.request.user,
                    shipping_address=address,
                    total_price=total_price,
                    coupon=coupon,
                    discount_amount=discount_amount,
                    status=OrderStatusType.PENDING,
                )

                # ----------------------
                # Coupon Usage
                # ----------------------

                if coupon:
                    CouponUsage.objects.create(
                        user=self.request.user,
                        coupon=coupon,
                        order=order,
                    )

                # ----------------------
                # بررسی اولیه موجودی
                # ----------------------

                for item in cart_items:

                    product = Product.objects.get(pk=item.product_id)

                    if item.quantity > product.stock:

                        raise InsufficientStock(product.title)

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.final_price,
                    )

                # ----------------------
                # ایجاد Payment
                # ----------------------

                payment = Payment.objects.create(
                    order=order,
                    amount=total_price,
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

        # ----------------------
        # ZarinPal Request
        # ----------------------

        zarinpal = ZarinPal()

        callback_url = self.request.build_absolute_uri(reverse("order:payment_verify"))

        try:

            authority = zarinpal.payment_request(
                amount=payment.amount,
                callback_url=callback_url,
                description=(f"پرداخت سفارش #{order.id}"),
                mobile=getattr(
                    self.request.user,
                    "mobile",
                    None,
                ),
                email=self.request.user.email,
            )

        except Exception as e:

            print("ZARINPAL ERROR:", repr(e))

            payment.status = PaymentStatus.FAILED

            payment.save(update_fields=["status"])

            messages.error(
                self.request,
                f"خطا در اتصال به درگاه پرداخت: {e}",
            )

            return redirect("order:checkout")

        # ----------------------
        # Save Authority
        # ----------------------

        payment.authority = authority

        payment.save(update_fields=["authority"])

        # Coupon session دیگر لازم نیست
        self.request.session.pop(
            "applied_coupon_code",
            None,
        )

        # ----------------------
        # Redirect to ZarinPal
        # ----------------------

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

        total_price = cart.total_price

        context["addresses"] = UserAddress.objects.filter(user=self.request.user)

        context["total_price"] = total_price

        context["total_tax"] = total_price * Decimal("9") / Decimal("100")

        return context


class PaymentVerifyView(View):

    def get(self, request):

        authority = request.GET.get("Authority")

        status = request.GET.get("Status")

        if not authority:

            return JsonResponse(
                {"message": ("Authority not found.")},
                status=400,
            )

        # ----------------------
        # پیدا کردن Payment
        # ----------------------

        payment = get_object_or_404(
            Payment,
            authority=authority,
        )

        # ----------------------
        # جلوگیری از Verify دوباره
        # ----------------------

        if payment.status == PaymentStatus.SUCCESS:
            return redirect("order:completed")

        # ----------------------
        # کاربر پرداخت را لغو کرده
        # ----------------------

        if status != "OK":

            payment.status = PaymentStatus.FAILED

            payment.save(update_fields=["status"])

            return redirect("order:payment_failed")

        # ----------------------
        # Verify با زرین پال
        # ----------------------

        zarinpal = ZarinPal()

        try:

            result = zarinpal.payment_verify(
                amount=payment.amount,
                authority=authority,
            )

        except Exception:

            payment.status = PaymentStatus.FAILED

            payment.save(update_fields=["status"])

            return redirect("order:payment_failed")

        code = result.get(
            "data",
            {},
        ).get("code")

        # ----------------------
        # Payment موفق
        # ----------------------

        if code in [100, 101]:

            with transaction.atomic():

                payment.status = PaymentStatus.SUCCESS

                payment.ref_id = result["data"].get("ref_id")

                payment.save(
                    update_fields=[
                        "status",
                        "ref_id",
                    ]
                )

                order = payment.order

                # ----------------------
                # کم کردن موجودی
                # ----------------------

                for item in order.items.all():

                    product = Product.objects.select_for_update().get(
                        pk=item.product_id
                    )

                    if item.quantity > product.stock:

                        # پرداخت موفق شده
                        # ولی موجودی کافی نیست
                        raise InsufficientStock(product.title)

                    product.stock -= item.quantity

                    product.save(update_fields=["stock"])

                # ----------------------
                # تغییر وضعیت Order
                # ----------------------

                order.status = OrderStatusType.PAID

                order.save(update_fields=["status"])

                # ----------------------
                # خالی کردن Cart
                # ----------------------

                cart = Cart.objects.filter(user=order.user).first()

                if cart:

                    cart.items.all().delete()

            return redirect("order:completed")

        # ----------------------
        # Payment Failed
        # ----------------------

        payment.status = PaymentStatus.FAILED

        payment.save(update_fields=["status"])

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
