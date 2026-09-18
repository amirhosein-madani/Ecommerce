from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from cart.messages import CartMessages
from cart.utils import get_cart
from products.models import Product

from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    CartUpdateSerializer,
)


class CartDetailAPIView(GenericAPIView):

    def get(self, request):
        cart = get_cart(request)

        items = [
            {
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "price": item["price"],
                "total_price": item["total_price"],
            }
            for item in cart
        ]

        serializer = CartSerializer(
            data={
                "items": items,
                "total_quantity": len(cart),
                "total_price": cart.get_total_price(),
            }
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


class AddToCartAPIView(GenericAPIView):
    serializer_class = AddToCartSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        product = get_object_or_404(
            Product.objects.published(),
            id=product_id,
        )

        cart = get_cart(request)

        current_quantity = cart.get_quantity(product.pk)

        if current_quantity + quantity > product.stock:
            return Response(
                {"error": CartMessages.NOT_ENOUGH_STOCK},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart.add(
            product.pk,
            quantity,
        )

        return Response(
            {
                "success": True,
                "message": CartMessages.PRODUCT_ADDED,
                "cart_count": len(cart),
                "total_quantity": len(cart),
                "total_price": cart.get_total_price(),
            },
            status=status.HTTP_200_OK,
        )


class CartUpdateAPIView(GenericAPIView):
    serializer_class = CartUpdateSerializer

    def patch(self, request, product_id):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data["quantity"]

        product = get_object_or_404(
            Product.objects.published(),
            id=product_id,
        )

        cart = get_cart(request)

        if quantity > product.stock:
            return Response(
                {"error": CartMessages.NOT_ENOUGH_STOCK},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart.update(
            product_id=product_id,
            quantity=quantity,
        )

        item_total = product.final_price * quantity

        return Response(
            {
                "success": True,
                "message": CartMessages.PRODUCT_INCREASED,
                "item_total": item_total,
                "cart_count": len(cart),
                "total_quantity": len(cart),
                "cart_total_price": cart.get_total_price(),
            },
            status=status.HTTP_200_OK,
        )


class CartRemoveAPIView(GenericAPIView):

    def delete(self, request, product_id):

        cart = get_cart(request)

        product = get_object_or_404(
            Product.objects.published(),
            id=product_id,
        )

        cart.remove(product.pk)

        return Response(
            {
                "success": True,
                "message": CartMessages.PRODUCT_REMOVED,
                "cart_count": len(cart),
                "total_quantity": len(cart),
                "cart_total_price": cart.get_total_price(),
            },
            status=status.HTTP_200_OK,
        )


class ClearCartAPIView(GenericAPIView):

    def delete(self, request):

        cart = get_cart(request)

        cart.clear()

        return Response(
            {
                "success": True,
                "message": CartMessages.CART_CLEARED,
                "cart_count": len(cart),
                "total_quantity": len(cart),
                "cart_total_price": cart.get_total_price(),
            },
            status=status.HTTP_200_OK,
        )
