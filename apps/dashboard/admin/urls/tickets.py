from django.urls import path

from dashboard.admin import views

urlpatterns = [
    path("ticketss-list/", views.tickets.TicketListView.as_view(), name="ticket_list"),
    path(
        "ticketss-update/<int:pk>/",
        views.tickets.TicketUpdateView.as_view(),
        name="ticket_update",
    ),
    path(
        "ticketss-delete/<int:pk>/",
        views.tickets.TicketDeleteView.as_view(),
        name="ticket_delete",
    ),
]
