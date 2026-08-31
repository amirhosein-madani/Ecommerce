from django.views.generic import DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from dashboard.permissions import HasAdminAccessPermission
from website.models.tickets import Ticket


class TicketListView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    ListView,
):

    template_name = "dashboard/admin/newsletters/newsletter-list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_items"] = self.object_list.count()
        return context

    # -----------------------------
    # Pagination
    # -----------------------------
    def get_queryset(self):

        queryset = Ticket.objects.all()
        search_q = self.request.GET.get("q")

        if search_q:
            queryset = queryset.filter(email__icontains=search_q)

        return queryset

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get("page_size")

        if page_size:
            try:
                page_size = int(page_size)

            except ValueError:
                return self.paginate_by

            if page_size in [
                5,
                10,
                20,
                30,
                50,
            ]:
                return page_size

        return self.paginate_by


class TicketDeleteieView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    model = Ticket
    template_name = "dashboard/admin/newsletters/newsletter-delete.html"
    success_url = reverse_lazy("dashboard:admin:newsletter_list")
    success_message = _("ایمیل با موفقیت حذف شد")
