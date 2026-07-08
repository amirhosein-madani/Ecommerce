from django.views.generic import ListView, DeleteView
from .models import Product, ProductStatusType, Category
from django.shortcuts import get_object_or_404

# Create your views here.


class ProductListView(ListView):
    """
    this is a view to show a list of products
    """

    template_name = "product/product-grid.html"
    queryset = Product.objects.filter(status=ProductStatusType.PUBLISH)
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["total_items"] = context["paginator"].count
        return context


class ProductDetailView(DeleteView):
    queryset = Product.objects.filter(status=ProductStatusType.PUBLISH)
    template_name = "product/product-detail.html"


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
