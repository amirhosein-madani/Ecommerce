from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, login
from .serializers import *
from templated_email import send_templated_mail
from ...models import Profile
from .permissions import IsNotAuthenticated

User = get_user_model()


class RegisterationAPIView(GenericAPIView):
    """
    this is a view for register a user
    """

    serializer_class = RegisterationSerializer
    permission_classes = [IsNotAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        email = serializer.validated_data["email"]

        user = get_object_or_404(User, email=email)
        token = self.get_token_for_user(user)
        access_token = token["access_token"]

        send_templated_mail(
            template_name="test-email",
            from_email="noreply@example.com",
            recipient_list=[user.email],
            context={
                "user": user,
                "site_name": "localhost",
                "access_token": access_token,
            },
        )

        return Response(
            {
                "details": (
                    f"Account created for {user.username}. Verification email sent to "
                    f"{email}. you need to verify to have full access to our site"
                )
            },
            status=status.HTTP_201_CREATED,
        )

    def get_token_for_user(self, user):

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return {"access_token": access_token}


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

            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            user = User.objects.get(id=user_id)
            user.is_verified = True
            user.save()

            login(request, user)

            return Response(
                {"details": "Email verified successfully"}, status=status.HTTP_200_OK
            )

        except Exception:

            return Response(
                {"details": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
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

        token = self.get_token_for_user(user)
        access_token = token["access_token"]

        send_templated_mail(
            template_name="test-email",
            from_email="noreply@example.com",
            recipient_list=[user.email],
            context={
                "user": user,
                "site_name": "localhost",
                "access_token": access_token,
            },
        )

        return Response(
            {"details": f"Verification email sent to {user.email}."},
            status=status.HTTP_200_OK,
        )

    def get_token_for_user(self, user):

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return {"access_token": access_token}


class ResetPasswordRequestApiView(GenericAPIView):
    permission_classes = [IsNotAuthenticated]
    serializer_class = SendEmailSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = self.get_token_for_user(user)
        access_token = token["access_token"]

        send_templated_mail(
            template_name="reset-password",
            from_email="noreply@example.com",
            recipient_list=[user.email],
            context={
                "user": user,
                "site_name": "localhost",
                "access_token": access_token,
            },
        )
        return Response(
            {"details": f"we sent a email to {user.email}"}, status=status.HTTP_200_OK
        )

    def get_token_for_user(self, user):

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return {"access_token": access_token}


class ResetPasswordApiView(GenericAPIView):

    serializer_class = ResetPasswordSerializer
    permission_classes = [IsNotAuthenticated]

    def post(self, request, token, *args, **kwargs):

        try:

            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)

        except (TokenError, InvalidToken):

            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "user does not exsit"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)

        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )
