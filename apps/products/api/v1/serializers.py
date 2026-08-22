from rest_framework import serializers
from products.models import Product, Category


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


class Productserializer(BaseSerializer):
    category = serializers.SlugRelatedField(
        slug_field="name", many=True, queryset=Category.objects.all()
    )
    final_price = serializers.ReadOnlyField()
    is_published = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "brief_description",
            "absolute_url",
            "category",
            "final_price",
            "image",
            "status",
            "discount_percent",
            "is_discounted",
            "is_published",
            "is_available",
            "stock",
            "is_discounted",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if request:
            kwargs = request.parser_context.get("kwargs", {})

            if kwargs.get("pk"):
                data.pop("absolute_url", None)
            else:
                data.pop("description", None)

        return data


class CategorySerializer(BaseSerializer):

    class Meta:
        model = Category
        fields = ["name", "is_active", "image", "absolute_url"]
