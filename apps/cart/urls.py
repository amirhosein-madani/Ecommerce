from django.urls import path
from cart.views import AddToCartView, CartView

app_name = "cart"

urlpatterns = [
    path(
        "add-product-to-cart/<int:product_id>/",
        AddToCartView.as_view(),
        name="add_to_cart",
    ),
    path("", CartView.as_view(), name="cart"),
]
