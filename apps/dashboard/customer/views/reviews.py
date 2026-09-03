from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


from dashboard.permissions import HasCustomerAccessPermission
from reviews.models import Review, ReviewStatus


class ReviewListView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    ListView,
):

    template_name = "dashboard/customer/reviews/review-list.html"
    paginate_by = 10

    def get_queryset(self):

        queryset = Review.objects.filter(user=self.request.user)

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

        context["total_items"] = context["paginator"].count
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


class ReviewDetailView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    DetailView,
):

    template_name = "dashboard/customer/reviews/review-detail.html"

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related(
            "product", "user"
        )
