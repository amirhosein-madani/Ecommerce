from django.urls import path
from order import views

app_name = "order"

urlpatterns = [
    path("checkout/", views.CheckOutView.as_view(), name="checkout"),
]
