from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from order.models.orders import UserAddress
from .serializers import UserAddressSerializer, CouponSerializer
from .permissions import IsCustomer
from order.models.coupons import Coupon


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


class CouponModelViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
