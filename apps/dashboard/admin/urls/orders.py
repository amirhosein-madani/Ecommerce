from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path("order-list/", views.orders.OrderListView.as_view(), name="order_list"),
    path(
        "order-update/<int:pk>/",
        views.orders.OrderUpdateView.as_view(),
        name="order_update",
    ),
    path(
        "order-invoice/<int:pk>/",
        views.orders.OrderInvoiceView.as_view(),
        name="order_invoice",
    ),
]
