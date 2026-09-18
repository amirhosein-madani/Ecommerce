from rest_framework import serializers


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(
        default=1,
        min_value=1,
    )


class CartUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1,
    )


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=0,
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=0,
    )


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
    )
