from django.urls import path
from dashboard.admin.views import AdminDashboardHomeView, AdminSecurityEditView

app_name = "admin"

urlpatterns = [
    path("home/", AdminDashboardHomeView.as_view(), name="home"),
    path("security-edit/", AdminSecurityEditView.as_view(), name="security_edit"),
]
