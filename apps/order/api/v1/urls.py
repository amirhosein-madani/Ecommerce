from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    UserAddressModelViewSet,
    CouponModelViewSet,
    CheckOutAPIView,
    ValidateCouponAPIView,
)

router = DefaultRouter()

router.register(r"address", UserAddressModelViewSet, basename="address")
router.register(r"coupon", CouponModelViewSet, basename="coupon")

urlpatterns = [
    path("checkout/", CheckOutAPIView.as_view(), name="api-checkout"),
    path(
        "validate-coupon/", ValidateCouponAPIView.as_view(), name="api-validate-coupon"
    ),
]
urlpatterns += router.urls
