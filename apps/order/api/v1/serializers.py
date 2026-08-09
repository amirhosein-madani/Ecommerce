from rest_framework import serializers
from order.models.orders import UserAddress


class BaseSerializer(serializers.ModelSerializer):

    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_url())

    def to_representation(self, instance):
        """
        this is a function for overwrite fields to show
        """

        request = self.context.get("request")
        data = super().to_representation(instance)

        if request.parser_context.get("kwargs").get("pk"):
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
