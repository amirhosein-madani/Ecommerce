from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path("users-list/", views.users.UserListView.as_view(), name="user_list"),
    path(
        "users-update/<int:pk>/",
        views.users.UserUpdateView.as_view(),
        name="user_edit",
    ),
    path(
        "users-delete/<int:pk>/",
        views.users.UserDeleteView.as_view(),
        name="user_delete",
    ),
]
