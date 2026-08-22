from rest_framework import serializers
from order.models.orders import UserAddress, Order, OrderItem
from order.models.coupons import Coupon
from products.models import Category, Product


class BaseSerializer(serializers.ModelSerializer):

    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_url())

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if request:
            kwargs = request.parser_context.get("kwargs", {})

            if kwargs.get("pk"):
                data.pop("absolute_url", None)

        return data


class UserAddressSerializer(BaseSerializer):

    class Meta:
        model = UserAddress
        fields = [
            "id",
            "address_name",
            "address",
            "state",
            "city",
            "zip_code",
            "absolute_url",
        ]

    def create(self, validated_data):

        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class CouponSerializer(BaseSerializer):

    usage_count = serializers.ReadOnlyField()
    categories = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Category.objects.all()
    )
    products = serializers.SlugRelatedField(
        many=True, slug_field="title", queryset=Product.objects.all()
    )

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "discount",
            "minimum_order_price",
            "max_discount",
            "products",
            "categories",
            "max_usage",
            "usage_count",
            "is_active",
            "absolute_url",
            "expires_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "usage_count",
            "created_at",
        ]


class ValidateCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)


class CheckOutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    coupon_code = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate_address_id(self, value):
        user = self.context["request"].user
        if not UserAddress.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("این آدرس متعلق به شما نیست.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_title", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "shipping_address",
            "total_price",
            "coupon",
            "discount_amount",
            "items",
            "created_at",
        ]
        read_only_fields = fields
