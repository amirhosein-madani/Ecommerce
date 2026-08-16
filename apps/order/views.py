from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from accounts.mixins import LoginRequiredMixin
from cart.models import Cart
from dashboard.permissions import HasCustomerAccessPermission
from order.forms import CheckOutForm
from order.models.coupons import Coupon, CouponUsage
from order.models.orders import Order, OrderItem, UserAddress
from order.services import (
    CouponNotApplicable,
    InsufficientStock,
    validate_and_apply_coupon,
)
from products.models import Product


class ValidateCouponView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, request):
        code = request.POST.get("code", "").strip()
        coupon = Coupon.objects.filter(code=code, is_active=True).first()

        if not coupon:
            return JsonResponse({"message": "کد تخفیف معتبر نیست."}, status=400)

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related("product").all()

        try:
            eligible_total, discount_amount = validate_and_apply_coupon(
                request.user, coupon, cart_items
            )
        except CouponNotApplicable as e:
            return JsonResponse({"message": str(e)}, status=400)

        total_price = cart.total_price - discount_amount
        total_tax = total_price * Decimal("9") / Decimal("100")

        request.session["applied_coupon_code"] = coupon.code

        return JsonResponse(
            {
                "message": f"کد تخفیف با موفقیت اعمال شد ({coupon.discount}%)",
                "total_price": total_price,
                "total_tax": total_tax,
            }
        )


class CheckOutView(LoginRequiredMixin, HasCustomerAccessPermission, FormView):
    template_name = "order/checkout.html"
    form_class = CheckOutForm
    success_url = reverse_lazy("order:completed")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_coupon(self):
        code = self.request.session.get("applied_coupon_code")
        if not code:
            return None
        return Coupon.objects.filter(code=code, is_active=True).first()

    def form_valid(self, form):
        address = get_object_or_404(
            UserAddress, user=self.request.user, pk=form.cleaned_data["address_id"]
        )
        cart = get_object_or_404(Cart, user=self.request.user)
        cart_items = cart.items.select_related("product").all()

        if not cart_items.exists():
            messages.warning(self.request, "سبد خرید شما خالی است.")
            return self.form_invalid(form)

        coupon = self.get_coupon()

        try:
            eligible_total = None
            discount_amount = Decimal("0")

            if coupon:
                eligible_total, discount_amount = validate_and_apply_coupon(
                    self.request.user, coupon, cart_items
                )

            with transaction.atomic():
                order = Order.objects.create(
                    user=self.request.user,
                    shipping_address=address,
                    total_price=cart.total_price,
                )

                if coupon:
                    order.total_price -= discount_amount
                    order.coupon = coupon
                    order.discount_amount = discount_amount
                    order.save(
                        update_fields=["total_price", "coupon", "discount_amount"]
                    )

                    CouponUsage.objects.create(
                        user=self.request.user, coupon=coupon, order=order
                    )

                for item in cart_items:
                    product = Product.objects.select_for_update().get(
                        pk=item.product_id
                    )

                    if item.quantity > product.stock:
                        raise InsufficientStock(product.title)

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.final_price,
                    )

                    product.stock -= item.quantity
                    product.save(update_fields=["stock"])

                cart_items.delete()

        except CouponNotApplicable as e:
            messages.warning(self.request, str(e))
            return self.form_invalid(form)

        except InsufficientStock as e:
            messages.warning(self.request, f"موجودی محصول «{e}» کافی نیست.")
            cart_items.delete()
            return self.form_invalid(form)

        self.request.session.pop("applied_coupon_code", None)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = get_object_or_404(Cart, user=self.request.user)
        total_price = cart.total_price

        context["addresses"] = UserAddress.objects.filter(user=self.request.user)
        context["total_price"] = total_price
        context["total_tax"] = total_price * Decimal("9") / Decimal("100")

        return context


class OrderCompletedView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/completed.html"
