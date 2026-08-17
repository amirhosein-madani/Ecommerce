from django.urls import path

# from rest_framework.authtoken.views import ObtainAuthToken

from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    #  registeration
    path("register/", RegisterationAPIView.as_view(), name="register"),
    # change password
    path("change-password/", ChangePasswordApiView.as_view(), name="change_password"),
    # reset password
    path(
        "request-to-reset-password/",
        ResetPasswordRequestApiView.as_view(),
        name="request_to_reset_password",
    ),
    path(
        "reset-password/<str:token>",
        ResetPasswordApiView.as_view(),
        name="reset_password",
    ),
    # login token
    path("token-login/", CustomObtainAuthToken.as_view(), name="token-login"),
    path("token-logout/", CustomDiscardAuthToken.as_view(), name="token-logout"),
    # activation
    path(
        "email-verification/<str:token>",
        VerificationApiView.as_view(),
        name="email-verification",
    ),
    # resend activation
    path(
        "resend-email-verification/",
        ResendVerificationApiView.as_view(),
        name="resend-verification",
    ),
    # path('activation/resend/')
    # login jwt
    path("jwt/create/", CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    # profile
    path("profile/", ProfileApiView.as_view(), name="user_profile"),
]
