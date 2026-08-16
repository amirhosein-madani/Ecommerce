from rest_framework.routers import DefaultRouter
from .views import UserAddressModelViewSet, CouponModelViewSet

router = DefaultRouter()

router.register(r"address", UserAddressModelViewSet, basename="address")
router.register(r"coupon", CouponModelViewSet, basename="coupon")


urlpatterns = router.urls
