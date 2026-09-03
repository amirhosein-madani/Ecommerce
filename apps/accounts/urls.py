from django.urls import path
from .views import (
    LoginView,
    user_logout,
    PasswordResetRequestView,
    ResetPasswordView,
    SignUpView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", user_logout, name="logout"),
    path(
        "request-to-reset-password",
        PasswordResetRequestView.as_view(),
        name="request_to_reset_password",
    ),
    path(
        "reset-password/<uidb64>/<token>/",
        ResetPasswordView.as_view(),
        name="reset_password_confirm",
    ),
    path("signup/", SignUpView.as_view(), name="signup"),
    # path("api/v1/", include("accounts.api.v1.urls")),
    # path('api/v2/' , include('djoser.urls')),
    # path('api/v2/' , include('djoser.urls.jwt')),
]
