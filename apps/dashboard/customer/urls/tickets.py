from django.urls import path

from dashboard.customer import views


urlpatterns = [
    path(
        "tickets-list/",
        views.tickets.TicketListView.as_view(),
        name="ticket_list",
    ),

    path(
        "ticket/<int:pk>/",
        views.tickets.TicketDetailView.as_view(),
        name="ticket_detail",
    ),
]