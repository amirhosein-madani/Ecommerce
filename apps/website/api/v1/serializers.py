from rest_framework import serializers
from website.models import Newsletter
from website.models.tickets import Ticket, TicketMessage
from products.models import Product, ProductStatusType
from website.models.wishlists import Wishlist
from accounts.models import UserType
from order.models import Order


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


class TicketMessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = TicketMessage
        fields = ["id", "ticket", "sender", "message", "is_staff_reply", "created_at"]
        read_only_fields = ["sender", "is_staff_reply", "created_at"]

    def validate_ticket(self, value):
        request = self.context["request"]
        is_staff = request.user.user_type in [UserType.ADMIN, UserType.SUPERUSER]
        if not is_staff and value.user_id != request.user.id:
            raise serializers.ValidationError("this ticket does not exsit.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["sender"] = request.user
        validated_data["is_staff_reply"] = request.user.user_type in [
            UserType.ADMIN,
            UserType.SUPERUSER,
        ]
        return super().create(validated_data)


class TicketSerializer(serializers.ModelSerializer):
    """
    this is a serializer based on TicketModel
    """

    user = serializers.ReadOnlyField(source="user.username")
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), required=False, allow_null=True
    )
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "user",
            "order",
            "subject",
            "status",
            "category",
            "priority",
            "status",
            "created_at",
            "updated_at",
            "closed_at",
            "messages",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "closed_at",
            "messages",
        ]

    def __init__(self, *args, **kwargs):
        """
        Restrict the order field to orders belonging to the
        currently authenticated user.

        This prevents a user from associating a ticket with
        another user's order.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["order"].queryset = Order.objects.filter(user=request.user)

        if request.user.user_type not in [
            UserType.ADMIN,
            UserType.SUPERUSER,
        ]:
            self.fields["status"].read_only = True

    def create(self, validated_data):
        """
        Associate the newly created ticket with the authenticated user.

        The user field is not accepted from the client and is populated
        from the request context instead.
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class WishListSerializer(serializers.ModelSerializer):

    products = serializers.SlugRelatedField(
        slug_field="title",
        many=True,
        queryset=Product.objects.filter(status=ProductStatusType.PUBLISH),
    )
    user = serializers.ReadOnlyField(source="user.username")
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Wishlist
        fields = ["id", "user", "products", "updated_at"]
