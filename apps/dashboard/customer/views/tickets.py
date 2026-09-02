from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from dashboard.permissions import HasCustomerAccessPermission
from website.models.tickets import Ticket, TicketMessage


class TicketListView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    ListView,
):
    model = Ticket
    template_name = "dashboard/customer/tickets/ticket-list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Ticket.objects.filter(
            user=self.request.user
        )

        search_q = self.request.GET.get("q")

        if search_q:
            queryset = queryset.filter(
                subject__icontains=search_q
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.object_list.count()
        return context

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get("page_size")

        if page_size:
            try:
                page_size = int(page_size)
            except ValueError:
                return self.paginate_by

            if page_size in [5, 10, 20, 30, 50]:
                return page_size

        return self.paginate_by


class TicketDetailView(
    LoginRequiredMixin,
    HasCustomerAccessPermission,
    DetailView,
):
    model = Ticket
    template_name = "dashboard/customer/tickets/ticket-detail.html"

    def get_queryset(self):
        return Ticket.objects.filter(
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["ticket_messages"] = (
            self.object.messages
            .select_related("sender")
            .order_by("created_at")
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        reply_message = request.POST.get(
            "reply_message",
            ""
        ).strip()

        if reply_message:
            TicketMessage.objects.create(
                ticket=self.object,
                sender=request.user,
                message=reply_message,
                is_staff_reply=False,
            )

            messages.success(
                request,
                _("پاسخ شما ثبت شد.")
            )

        return redirect(
            "dashboard:customer:ticket_detail",
            pk=self.object.pk,
        )