from django.urls import path
from order import views

app_name = "order"

urlpatterns = [
    path("checkout/", views.CheckOutView.as_view(), name="checkout"),
    path("completed/", views.OrderCompletedView.as_view(), name="completed"),
    path(
        "validate-coupon/", views.ValidateCouponView.as_view(), name="validate-coupon"
    ),
]
