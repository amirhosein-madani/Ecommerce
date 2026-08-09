from rest_framework.routers import DefaultRouter
from .views import UserAddressModelViewSet

router = DefaultRouter()

router.register(r"address", UserAddressModelViewSet, basename="address")


urlpatterns = router.urls
