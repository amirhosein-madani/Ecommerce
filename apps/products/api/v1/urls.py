from rest_framework.routers import DefaultRouter
from .views import ProductModelViewSet, CategoryModelViewSet

router = DefaultRouter()


router.register(r"product", ProductModelViewSet, basename="product")
router.register(r"category", CategoryModelViewSet, basename="category")

urlpatterns = router.urls
