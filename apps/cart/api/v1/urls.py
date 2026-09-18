from django.urls import path

from .views import (
    AddToCartAPIView,
    CartDetailAPIView,
    CartRemoveAPIView,
    CartUpdateAPIView,
    ClearCartAPIView,
)

urlpatterns = [
    path(
        "",
        CartDetailAPIView.as_view(),
        name="cart-detail",
    ),
    path(
        "items/",
        AddToCartAPIView.as_view(),
        name="cart-add",
    ),
    path(
        "items/<int:product_id>/",
        CartUpdateAPIView.as_view(),
        name="cart-update",
    ),
    path(
        "items/<int:product_id>/remove/",
        CartRemoveAPIView.as_view(),
        name="cart-remove",
    ),
    path(
        "clear/",
        ClearCartAPIView.as_view(),
        name="cart-clear",
    ),
]
