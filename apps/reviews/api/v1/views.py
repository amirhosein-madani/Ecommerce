from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import viewsets
from order.api.v1.permissions import IsAdmin, IsCustomer

from reviews.models import Review, ReviewStatus

from .serializers import CustomerReviewSerializer, AdminReviewSerializer


class ReviewListCreateAPIView(ListCreateAPIView):
    """Public-facing: only approved reviews, no status filter."""

    serializer_class = CustomerReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product"]
    queryset = Review.objects.filter(status=ReviewStatus.APPROVED)


class ReviewRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    """A user can view/delete their own review regardless of its status."""

    serializer_class = CustomerReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


class CustomerReviewListAPIView(ListAPIView):
    """Customer's own reviews, filterable by status and product."""

    serializer_class = CustomerReviewSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "product"]

    def get_queryset(self):

        return Review.objects.filter(user=self.request.user)


class AdminReviewViewSet(viewsets.ModelViewSet):

    queryset = Review.objects.all()
    serializer_class = AdminReviewSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "product"]
