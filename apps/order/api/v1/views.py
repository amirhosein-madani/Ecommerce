from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from order.models.orders import UserAddress
from .serializers import UserAddressSerializer
from .permissions import IsCustomer


class UserAddressModelViewSet(viewsets.ModelViewSet):

    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["state", "city"]
    search_fields = [
        "address_name",
        "city",
        "state",
        "address",
    ]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
