from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path("product-list/", views.products.ProductListView.as_view(), name="product_list")
]
