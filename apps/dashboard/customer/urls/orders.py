from django.urls import path

from dashboard.customer import views

urlpatterns = [
    path(
        "order-list/", views.orders.CustomerOrderListView.as_view(), name="order_list"
    ),
    path(
        "orders/<int:pk>/",
        views.orders.CustomerOrderDetailView.as_view(),
        name="order_detail",
    ),
]
