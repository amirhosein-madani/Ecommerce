from decimal import Decimal

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.shortcuts import get_object_or_404
from order.models.orders import Order, OrderItem, UserAddress
from .serializers import (
    UserAddressSerializer,
    CouponSerializer,
    CheckOutSerializer,
    OrderSerializer,
    ValidateCouponSerializer,
)
from .permissions import IsCustomer, IsAdmin
from order.models.coupons import Coupon, CouponUsage
from order.services import (
    CouponNotApplicable,
    InsufficientStock,
    validate_and_apply_coupon,
)
from cart.models import Cart
from products.models import Product


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
    permission_classes = [IsAuthenticated, IsAdmin]


class ValidateCouponAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = ValidateCouponSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"].strip()

        coupon = Coupon.objects.filter(code=code, is_active=True).first()
        if not coupon:
            return Response(
                {"detail": "کد تخفیف معتبر نیست."}, status=status.HTTP_400_BAD_REQUEST
            )

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related("product").all()

        try:
            eligible_total, discount_amount = validate_and_apply_coupon(
                request.user, coupon, cart_items
            )
        except CouponNotApplicable as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        total_price = cart.total_price - discount_amount
        total_tax = total_price * Decimal("9") / Decimal("100")

        return Response(
            {
                "detail": f"کد تخفیف با موفقیت اعمال شد ({coupon.discount}%)",
                "discount_amount": discount_amount,
                "total_price": total_price,
                "total_tax": total_tax,
            },
            status=status.HTTP_200_OK,
        )


class CheckOutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    serializer_class = CheckOutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        address = get_object_or_404(
            UserAddress, user=request.user, pk=serializer.validated_data["address_id"]
        )
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related("product").all()

        if not cart_items.exists():
            return Response(
                {"detail": "سبد خرید شما خالی است."}, status=status.HTTP_400_BAD_REQUEST
            )

        coupon_code = serializer.validated_data.get("coupon_code")
        coupon = (
            Coupon.objects.filter(code=coupon_code, is_active=True).first()
            if coupon_code
            else None
        )

        try:
            discount_amount = Decimal("0")

            if coupon:
                eligible_total, discount_amount = validate_and_apply_coupon(
                    request.user, coupon, cart_items
                )

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=address,
                    total_price=cart.total_price,
                )

                if coupon:
                    order.total_price -= discount_amount
                    order.coupon = coupon
                    order.discount_amount = discount_amount
                    order.save(
                        update_fields=["total_price", "coupon", "discount_amount"]
                    )

                    CouponUsage.objects.create(
                        user=request.user, coupon=coupon, order=order
                    )

                for item in cart_items:
                    product = Product.objects.select_for_update().get(
                        pk=item.product_id
                    )

                    if item.quantity > product.stock:
                        raise InsufficientStock(product.title)

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.final_price,
                    )

                    product.stock -= item.quantity
                    product.save(update_fields=["stock"])

                cart_items.delete()

        except CouponNotApplicable as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except InsufficientStock as e:
            return Response(
                {"detail": f"موجودی محصول «{e}» کافی نیست."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
