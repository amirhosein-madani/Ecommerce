from django.shortcuts import get_object_or_404

from django.views.generic import ListView, DetailView
from .models import Product, ProductStatusType, Category
from reviews.models import Review, ReviewStatus


class ProductListView(ListView):
    """
    this is a view to show a list of products
    """

    template_name = "product/product-grid.html"
    paginate_by = 9

    def get_queryset(self):
        queryset = Product.objects.published().with_final_price()

        category_id = self.request.GET.get("category_id")
        search_q = self.request.GET.get("q")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        order_by = self.request.GET.get("order_by")
        is_discounted = self.request.GET.get("is_discounted")

        if is_discounted:
            queryset = queryset.filter(is_discounted=True)

        if order_by:
            queryset = queryset.sort(order_by)

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if search_q:
            queryset = queryset.filter(title__icontains=search_q)

        if min_price:
            queryset = queryset.filter(annotated_final_price__gte=min_price)

        if max_price:
            queryset = queryset.filter(annotated_final_price__lt=max_price)

        return queryset

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get("page_size")

        if page_size:

            try:
                page_size = int(page_size)

            except ValueError:
                return self.paginate_by

            if page_size in [5, 10, 15, 20, 30]:
                return page_size

        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["total_items"] = context["paginator"].count
        return context


class ProductDetailView(DetailView):
    queryset = Product.objects.filter(status=ProductStatusType.PUBLISH)
    template_name = "product/product-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reviews = Review.objects.filter(
            product=self.object, status=ReviewStatus.APPROVED
        )

        review_count = reviews.count()

        reviews_count = {
            "rate_5": reviews.filter(rate=5).count(),
            "rate_4": reviews.filter(rate=4).count(),
            "rate_3": reviews.filter(rate=3).count(),
            "rate_2": reviews.filter(rate=2).count(),
            "rate_1": reviews.filter(rate=1).count(),
        }

        reviews_avg = {
            "rate_5": (
                (reviews_count["rate_5"] / review_count * 100) if review_count else 0
            ),
            "rate_4": (
                (reviews_count["rate_4"] / review_count * 100) if review_count else 0
            ),
            "rate_3": (
                (reviews_count["rate_3"] / review_count * 100) if review_count else 0
            ),
            "rate_2": (
                (reviews_count["rate_2"] / review_count * 100) if review_count else 0
            ),
            "rate_1": (
                (reviews_count["rate_1"] / review_count * 100) if review_count else 0
            ),
        }

        context["reviews"] = reviews
        context["reviews_count"] = reviews_count
        context["reviews_avg"] = reviews_avg

        return context


class CategoryDetailView(ListView):
    template_name = "product/category.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs["slug"],
            is_active=True,
        )

        return self.category.products.filter(
            status=ProductStatusType.PUBLISH
        ).prefetch_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context
