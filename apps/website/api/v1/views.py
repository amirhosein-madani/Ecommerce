from rest_framework.filters import OrderingFilter
from rest_framework.generics import (
    ListAPIView,
    RetrieveDestroyAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)
from django_filters.rest_framework import DjangoFilterBackend
from order.api.v1.permissions import IsAdmin
from .serializers import (
    Newsletterserializer,
    TicketMessageSerializer,
    TicketSerializer,
    WishListSerializer,
)
from products.api.v1.paginations import DefaultPagination
from website.models import Newsletter
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from website.models.tickets import Ticket, TicketMessage

from website.models.wishlists import Wishlist
from accounts.models import UserType


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


class TicketListCreateAPIView(ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status", "category", "priority"]
    search_fields = ["subject"]

    def get_queryset(self):
        if self.request.user.user_type in [UserType.ADMIN, UserType.SUPERUSER]:
            return Ticket.objects.all()
        return Ticket.objects.filter(user=self.request.user)


class TicketRetrieveDestroyAPIView(RetrieveUpdateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type in [UserType.ADMIN, UserType.SUPERUSER]:
            return Ticket.objects.all()
        return Ticket.objects.filter(user=self.request.user)


class TicketMessageListCreateAPIView(ListCreateAPIView):
    serializer_class = TicketMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = TicketMessage.objects.all()

        if self.request.user.user_type not in [
            UserType.ADMIN,
            UserType.SUPERUSER,
        ]:
            qs = qs.filter(ticket__user=self.request.user)

        return qs


class TicketMessageRetrieveAPIView(RetrieveAPIView):
    serializer_class = TicketMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = TicketMessage.objects.all()

        if self.request.user.user_type not in [
            UserType.ADMIN,
            UserType.SUPERUSER,
        ]:
            qs = qs.filter(ticket__user=self.request.user)

        return qs


class WishlistRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishListSerializer

    def get_object(self):
        return Wishlist.objects.get(user=self.request.user)
