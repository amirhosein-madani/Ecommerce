from django.urls import path

from dashboard.customer import views

urlpatterns = [
    path("home/", views.generals.CustomerDashboardHomeView.as_view(), name="home"),
    path(
        "security-edit/",
        views.generals.CustomerSecurityEditView.as_view(),
        name="security_edit",
    ),
]
