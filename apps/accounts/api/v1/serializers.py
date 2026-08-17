from rest_framework import serializers
from ...models import User, Profile
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterationSerializer(serializers.ModelSerializer):
    """
    this is a serializer to register users
    """

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "national_code", "password", "confirm_password"]

    def validate(self, attrs):

        if attrs.get("password") != attrs.get("confirm_password"):

            raise serializers.ValidationError({"detail": "passwords does not match"})

        try:

            validate_password(attrs.get("password"))

        except exceptions.ValidationError as e:

            raise serializers.ValidationError({"passwords": list(e.messages)})

        return super().validate(attrs)

    def create(self, validated_data):

        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to add extra content to the token response.
    """

    def validate(self, attrs):
        # Authenticate user and get token data
        validated_data = super().validate(attrs)

        # Check if user is verified after authentication
        if not self.user.is_verified:
            raise serializers.ValidationError({"detail": "This user is not verified."})

        # Add extra fields to response
        validated_data["email"] = self.user.email
        validated_data["user_id"] = self.user.id

        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    """
    this is a serializer to change user's password
    """

    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):

        user = self.context["request"].user

        if user.check_password(attrs.get("old_password")):

            if attrs.get("old_password") == attrs.get("new_password"):

                raise serializers.ValidationError(
                    {"detail": "this is your old password"}
                )

            if attrs.get("new_password") != attrs.get("confirm_password"):

                raise serializers.ValidationError(
                    {"detail": "passwords does not match"}
                )

            try:

                validate_password(attrs.get("new_password"))

            except exceptions.ValidationError as e:

                raise serializers.ValidationError({"passwords": list(e.messages)})

        else:

            raise serializers.ValidationError({"detail": "old_password is not correct"})

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """
    this is a serializer to show user's profile
    """

    user = serializers.CharField(read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class SendEmailSerializer(serializers.Serializer):
    """
    this is a serializer to resend a verification email to user
    """

    email = serializers.EmailField()

    def validate(self, attrs):

        email = attrs.get("email")

        try:

            user = User.objects.get(email=email)

        except User.DoesNotExist:

            raise serializers.ValidationError("this email does not match any user.")

        # if user.is_verified:

        # raise serializers.ValidationError("this user is already verified.")

        attrs["user"] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):

        user = self.context.get("user")
        if user and user.check_password(attrs.get("password")):
            raise serializers.ValidationError(
                {"detail": "New password cannot be the same as old password"}
            )

        if attrs.get("password") != attrs.get("confirm_password"):

            raise serializers.ValidationError({"detail": "passwords does not match"})

        try:

            validate_password(attrs.get("password"))

        except exceptions.ValidationError as e:

            raise serializers.ValidationError({"passwords": list(e.messages)})

        user.set_password(attrs.get("password"))
        user.save()
        return attrs
