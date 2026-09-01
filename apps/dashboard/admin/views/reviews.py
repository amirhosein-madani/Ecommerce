from django.views.generic import DeleteView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from dashboard.permissions import HasAdminAccessPermission
from reviews.models import Review, ReviewStatus


class ReviewListView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    ListView,
):

    template_name = "dashboard/admin/reviews/review-list.html"
    paginate_by = 10

    def get_queryset(self):

        queryset = Review.objects.all()

        # -----------------------------
        # Search
        # -----------------------------

        search_q = self.request.GET.get("q")

        if search_q:
            queryset = queryset.filter(product__title__icontains=search_q)

        # -----------------------------
        # Status Filter
        # -----------------------------

        status = self.request.GET.get("status")

        if status in ReviewStatus.values:
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

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_items"] = self.object_list.count()
        context["status_types"] = ReviewStatus.choices

        return context

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


class ReviewUpdateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    model = Review
    template_name = "dashboard/admin/reviews/review-edit.html"

    fields = [
        "status",
        "description",
    ]

    success_url = reverse_lazy("dashboard:admin:review_list")
    success_message = _("وضعیت نظر با موفقیت ویزایش شد.")


class ReviewDeleteView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    model = Review
    success_url = reverse_lazy("dashboard:admin:review_list")
    success_message = _("کامنت با موفقیت حذف شد")
