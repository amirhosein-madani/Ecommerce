from rest_framework import viewsets
from accounts.models import UserType
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from products.models import Product, Category
from products.models import ProductStatusType
from products.api.v1.serializers import CategorySerializer, Productserializer
from .permissions import IsAdminOrReadOnly
from .paginations import DefaultPagination


class ProductModelViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    pagination_class = DefaultPagination
    serializer_class = Productserializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "status", "is_discounted"]
    search_fields = ["title", "description", "brief_description"]
    ordering_fields = ["price", "created_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.user_type in [
            UserType.ADMIN,
            UserType.SUPERUSER,
        ]:
            return Product.objects.all()

        return Product.objects.filter(status=ProductStatusType.PUBLISH)
