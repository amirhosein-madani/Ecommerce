from rest_framework import serializers
from reviews.models import Review
from products.models import Product, ProductStatusType


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

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        product = attrs.get("product")

        if Review.objects.filter(
            user=user,
            product=product,
        ).exists():
            raise serializers.ValidationError(
                {"product": "You have already reviewed this product."}
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class CustomerReviewSerializer(BaseSerializer):

    user = serializers.ReadOnlyField(source="user.username")

    product = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Product.objects.filter(status=ProductStatusType.PUBLISH),
    )

    status = serializers.ReadOnlyField()

    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "description",
            "rate",
            "status",
            "created_at",
            "absolute_url",
            "updated_at",
        ]

    def get_absolute_url(self, obj):
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(f"/reviews/api/v1/reviews/{obj.pk}/")

        return f"/reviews/api/v1/reviews/{obj.pk}/"


class AdminReviewSerializer(BaseSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    product = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Product.objects.filter(status=ProductStatusType.PUBLISH),
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "description",
            "rate",
            "status",
            "created_at",
            "absolute_url",
            "updated_at",
        ]
