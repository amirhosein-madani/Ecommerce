from django.views.generic import FormView, TemplateView
from decimal import Decimal
from django.urls import reverse_lazy
from accounts.mixins import LoginRequiredMixin
from dashboard.permissions import HasCustomerAccessPermission
from order.models.orders import UserAddress
from order.forms import CheckOutForm
from cart.models import Cart


class CheckOutView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    FormView,
):
    template_name = "order/checkout.html"
    form_class = CheckOutForm
    success_url = reverse_lazy("order:completed")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = Cart.objects.get(user=self.request.user)

        total_price = cart.total_price

        context["addresses"] = UserAddress.objects.filter(user=self.request.user)

        context["total_price"] = total_price

        context["total_tax"] = total_price * Decimal("9") / Decimal("100")

        return context


class OrderCompletedView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    TemplateView,
):
    template_name = "order/completed.html"
