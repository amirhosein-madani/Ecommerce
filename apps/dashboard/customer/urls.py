from django.urls import path
from . import views

app_name = "customer"

urlpatterns = [
    path("home/", views.generals.CustomerDashboardHomeView.as_view(), name="home"),
    path("security-edit/", views.generals.CustomerSecurityEditView.as_view(), name="security_edit"),
    path("profile/edit/", views.profiles.CustomerProfileEditView.as_view(), name="profile_edit"),
    path(
        "profile/edit-image/", views.profiles.ProfileImageEditView.as_view(), name="profile_image_edit"
    ),
    path(
        "profile-edit/image/delete/",
        views.profiles.ProfileImageDeleteView.as_view(),
        name="profile_image_delete",
    ),
]
