from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path("home/", views.generals.AdminDashboardHomeView.as_view(), name="home"),
    path(
        "security-edit/",
        views.generals.AdminSecurityEditView.as_view(),
        name="security_edit",
    ),
]
