from django.urls import path
from dashboard.customer.views import CustomerDashboardHomeView

app_name = "customer"

urlpatterns = [
    path("home/", CustomerDashboardHomeView.as_view(), name="home"),
]
