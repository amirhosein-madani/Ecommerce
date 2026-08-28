from django.views.generic import (
    DetailView,
    ListView,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasCustomerAccessPermission
from order.models.orders import Order, OrderStatusType


class CustomerOrderListView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):

    template_name = "dashboard/customer/orders/order-list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)

        order_by = self.request.GET.get("order_by")
        search_q = self.request.GET.get("q")

        if search_q:
            try:
                order_id = int(search_q)
                queryset = queryset.filter(id=order_id)
            except ValueError:
                queryset = queryset.filter(
                    items__product__title__icontains=search_q
                ).distinct()

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        if order_by and order_by in ["created_at", "-created_at"]:
            queryset = queryset.order_by(order_by)

        return queryset.prefetch_related("items__product")

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get("page_size")

        if page_size:

            try:
                page_size = int(page_size)

            except ValueError:
                return self.paginate_by

            if page_size in [5, 10, 20, 30, 50]:
                return page_size

        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_types"] = OrderStatusType.choices
        context["total_items"] = self.object_list.count()
        return context


class CustomerOrderDetailView(
    LoginRequiredMixin, HasCustomerAccessPermission, DetailView
):
    model = Order
    template_name = "dashboard/customer/orders/order-detail.html"

    def get_queryset(self):

        return (
            Order.objects.filter(user=self.request.user)
            .select_related("user__profile", "coupon", "shipping_address")
            .prefetch_related("items__product")
        )
