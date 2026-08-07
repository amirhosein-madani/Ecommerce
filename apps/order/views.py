from django.views.generic import TemplateView
from accounts.mixins import LoginRequiredMixin
from dashboard.permissions import HasCustomerAccessPermission


class CheckOutView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/checkout.html"
