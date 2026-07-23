from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path(
        "product-list/", views.products.ProductListView.as_view(), name="product_list"
    ),
    path(
        "product-update/<int:pk>/",
        views.products.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "product-delete/<int:pk>/",
        views.products.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path(
        "create-product/",
        views.products.ProductCreateView.as_view(),
        name="product_create",
    ),
]
