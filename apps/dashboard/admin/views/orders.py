from django.views.generic import (
    UpdateView,
    ListView,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.messages.views import SuccessMessageMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import ProductUpdateForm, ProductImageForm
from order.models.orders import Order


class OrderListView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, ListView
):
    model = Order
    template_name = "dashboard/admin/orders/order-list.html"
    paginate_by = 10


class OrderUpdateView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView
):
    model = Order
