from rest_framework import serializers
from order.models.orders import UserAddress
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
