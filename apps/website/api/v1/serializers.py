from rest_framework import serializers
from website.models import Newsletter


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


class Newsletterserializer(BaseSerializer):

    class Meta:
        model = Newsletter
        fields = ["id", "email", "absolute_url", "created_at"]
