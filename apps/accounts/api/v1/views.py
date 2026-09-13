from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, login
from .serializers import *
from django.core.exceptions import ValidationError
from accounts.tasks import registration_email, reset_password_email
from ...models import Profile
from .permissions import IsNotAuthenticated
from accounts.models import EmailVerificationToken, PasswordResetToken

User = get_user_model()


class RegisterationAPIView(GenericAPIView):
    """Register a new user and dispatch a verification email asynchronously."""

    serializer_class = RegisterationSerializer
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        verification = EmailVerificationToken.objects.create(user=user)
        registration_email.delay(user.email, user.username, str(verification.token))

        return Response(
            {
                "details": (
                    f"Account created for {user.username}. Verification email sent to "
                    f"{user.email}. you need to verify to have full access to our site"
                )
            },
            status=status.HTTP_201_CREATED,
        )


class CustomObtainAuthToken(ObtainAuthToken):
    """
    this is a views to create a auth_token for a user
    """

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if not user.is_verified:
            return Response(
                {"details": "this user is not verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
                "email": user.email,
            }
        )


class CustomDiscardAuthToken(APIView):
    """
    this is a view to delete auth_token for a user
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception:
            return Response(
                {"detail": "user has no active token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    this is a view to create JWT token
    """

    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordApiView(GenericAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response({"details": "password updated"}, status=status.HTTP_200_OK)


class ProfileApiView(RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        return get_object_or_404(Profile, user=self.request.user)


class VerificationApiView(APIView):

    permission_classes = [IsNotAuthenticated]

    def get(self, request, token, *args, **kwargs):

        try:
            verification = EmailVerificationToken.objects.select_related("user").get(
                token=token
            )
        except (EmailVerificationToken.DoesNotExist, ValidationError):
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not verification.is_valid():
            return Response(
                {"detail": "Token expired or already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = verification.user
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        verification.mark_used()

        login(request, user)

        return Response(
            {"details": "Email verified successfully"}, status=status.HTTP_200_OK
        )


class ResendVerificationApiView(APIView):

    permission_classes = [IsNotAuthenticated]
    serializer_class = SendEmailSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if user.is_verified:
            return Response(
                {"detail": "this user is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        EmailVerificationToken.objects.filter(user=user, is_used=False).update(
            is_used=True
        )
        verification = EmailVerificationToken.objects.create(user=user)
        registration_email.delay(user.email, user.username, str(verification.token))

        return Response(
            {"details": f"Verification email sent to {user.email}."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordRequestApiView(GenericAPIView):
    permission_classes = [IsNotAuthenticated]
    serializer_class = SendEmailSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
        reset_token = PasswordResetToken.objects.create(user=user)
        reset_password_email.delay(user.email, user.username, str(reset_token.token))

        return Response(
            {"details": f"we sent a email to {user.email}"}, status=status.HTTP_200_OK
        )


class ResetPasswordApiView(GenericAPIView):

    serializer_class = ResetPasswordSerializer
    permission_classes = [IsNotAuthenticated]

    def post(self, request, token, *args, **kwargs):

        try:
            verification = PasswordResetToken.objects.select_related("user").get(
                token=token
            )
        except (PasswordResetToken.DoesNotExist, ValidationError):
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not verification.is_valid():
            return Response(
                {"detail": "Token expired or already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = verification.user
        serializer = self.serializer_class(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)

        verification.mark_used()

        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )
