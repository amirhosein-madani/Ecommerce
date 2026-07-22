from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path(
        "profile/edit/",
        views.profiles.AdminProfileEditView.as_view(),
        name="profile_edit",
    ),
    path(
        "profile/edit-image/",
        views.profiles.ProfileImageEditView.as_view(),
        name="profile_image_edit",
    ),
    path(
        "profile-edit/image/delete/",
        views.profiles.ProfileImageDeleteView.as_view(),
        name="profile_image_delete",
    ),
]
