from rest_framework.generics import RetrieveDestroyAPIView, ListAPIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import Newsletterserializer
from products.api.v1.paginations import DefaultPagination
from website.models import Newsletter
from order.api.v1.permissions import IsAdmin


class NewsletterListApiView(ListAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = Newsletterserializer
    permission_classes = [IsAdmin]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "email": ["in"],
    }
    ordering_fields = ["created_at"]


class NewsletterRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = Newsletterserializer
    permission_classes = [IsAdmin]
