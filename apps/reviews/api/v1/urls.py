from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ReviewListCreateAPIView,
    ReviewRetrieveDestroyAPIView,
    CustomerReviewListAPIView,
    AdminReviewViewSet,
)

router = DefaultRouter()

router.register(r"admin/reviews", AdminReviewViewSet, basename="admin-review")

urlpatterns = [
    # Public
    path(
        "reviews/",
        ReviewListCreateAPIView.as_view(),
        name="review-list-create",
    ),
    # Customer
    path(
        "reviews/me/",
        CustomerReviewListAPIView.as_view(),
        name="customer-review-list",
    ),
    path(
        "reviews/<int:pk>/",
        ReviewRetrieveDestroyAPIView.as_view(),
        name="review-retrieve-destroy",
    ),
]

urlpatterns += router.urls
