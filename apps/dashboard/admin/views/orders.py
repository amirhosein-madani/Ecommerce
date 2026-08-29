from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, UpdateView, DetailView

from dashboard.permissions import HasAdminAccessPermission
from order.models.orders import Order, OrderStatusType


class OrderListView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    ListView,
):
    model = Order
    template_name = "dashboard/admin/orders/order-list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.select_related(
            "user",
            "shipping_address",
            "coupon",
        ).prefetch_related("items__product")

        # -----------------------------
        # Search
        # -----------------------------

        search_q = self.request.GET.get("q", "").strip()

        if search_q:
            try:
                order_id = int(search_q)

                queryset = queryset.filter(id=order_id)

            except ValueError:
                queryset = queryset.filter(
                    Q(items__product__title__icontains=search_q)
                    | Q(user__username__icontains=search_q)
                ).distinct()

        # -----------------------------
        # Status Filter
        # -----------------------------

        status = self.request.GET.get("status")

        if status:
            queryset = queryset.filter(status=status)

        # -----------------------------
        # Ordering
        # -----------------------------

        order_by = self.request.GET.get("order_by")

        if order_by in [
            "created_at",
            "-created_at",
        ]:
            queryset = queryset.order_by(order_by)

        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    # -----------------------------
    # Pagination
    # -----------------------------

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get("page_size")

        if page_size:
            try:
                page_size = int(page_size)

            except ValueError:
                return self.paginate_by

            if page_size in [
                5,
                10,
                20,
                30,
                50,
            ]:
                return page_size

        return self.paginate_by

    # -----------------------------
    # Context
    # -----------------------------

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["status_types"] = OrderStatusType.choices

        context["total_items"] = self.object_list.count()

        # برای نگه داشتن فیلترها در template
        context["current_search"] = self.request.GET.get("q", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_order_by"] = self.request.GET.get(
            "order_by",
            "-created_at",
        )
        context["current_page_size"] = self.request.GET.get(
            "page_size",
            "10",
        )

        return context


class OrderUpdateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    model = Order

    fields = [
        "status",
    ]

    template_name = "dashboard/admin/orders/order-detail.html"

    context_object_name = "order"

    success_message = _("وضعیت سفارش #%(id)s با موفقیت به‌روزرسانی شد.")

    def get_success_message(self, cleaned_data):
        return self.success_message % {
            "id": self.object.pk,
        }

    def get_success_url(self):
        return reverse(
            "dashboard:admin:order_detail",
            kwargs={
                "pk": self.object.pk,
            },
        )


class OrderInvoiceView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    DetailView,
):
    model = Order
    template_name = "dashboard/admin/orders/order-invoice.html"
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects.select_related(
                "user__profile",
                "coupon",
                "shipping_address",
            )
            .prefetch_related(
                "items__product",
            )
            .exclude(
                status__in=[
                    OrderStatusType.PENDING,
                    OrderStatusType.CANCELED,
                ]
            )
        )
