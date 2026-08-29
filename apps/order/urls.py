from django.urls import path, include
from order import views

app_name = "order"

urlpatterns = [
    path("checkout/", views.CheckOutView.as_view(), name="checkout"),
    path("api/v1/", include("order.api.v1.urls")),
    path(
        "checkout/",
        views.CheckOutView.as_view(),
        name="checkout",
    ),
    path(
        "completed/",
        views.OrderCompletedView.as_view(),
        name="completed",
    ),
    path(
        "validate-coupon/",
        views.ValidateCouponView.as_view(),
        name="validate-coupon",
    ),
    path(
        "payment/verify/",
        views.PaymentVerifyView.as_view(),
        name="payment_verify",
    ),
    path(
        "payment/failed/",
        views.PaymentFailedView.as_view(),
        name="payment_failed",
    ),
]
