from django.urls import path
from products.views import ProductListView, ProductDetailView, CategoryDetailView

app_name = "product"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_grid"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
    path("<str:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
