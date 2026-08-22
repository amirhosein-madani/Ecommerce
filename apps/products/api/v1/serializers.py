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

    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "brief_description",
            "absolute_url",
            "category",
            "price",
            "image",
            "status",
            "discount_percent",
            "stock",
            "is_discounted",
        ]

class CategorySerializer(BaseSerializer):

    class Meta:
        model = Category
        fields = ["name", "is_active", "image" , 'absolute_url']
