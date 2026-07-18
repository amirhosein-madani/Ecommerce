from django.urls import path
from cart.views import AddToCartView, CartView, CartUpdateView, CartRemoveView

app_name = "cart"

urlpatterns = [
    path("add/<int:product_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("", CartView.as_view(), name="cart"),
    path("update/<int:product_id>/", CartUpdateView.as_view(), name="update_cart"),
    path(
        "remove/<int:product_id>/",
        CartRemoveView.as_view(),
        name="remove_product_from_cart",
    ),
]
