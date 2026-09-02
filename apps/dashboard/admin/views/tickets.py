from django.views.generic import DeleteView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


from dashboard.permissions import HasAdminAccessPermission
from website.models.tickets import Ticket, TicketMessage


class TicketListView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    ListView,
):
    model = Ticket
    template_name = "dashboard/admin/tickets/ticket-list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Ticket.objects.all()
        search_q = self.request.GET.get("q")

        if search_q:
            queryset = queryset.filter(subject__icontains=search_q)

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


class TicketUpdateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    model = Ticket
    template_name = "dashboard/admin/tickets/ticket-edit.html"
    fields = ["status", "category", "priority"]
    success_message = _("تیکت با موفقیت به‌روزرسانی شد.")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["status"].widget.attrs.update({"class": "form-select"})
        form.fields["category"].widget.attrs.update({"class": "form-select"})
        form.fields["priority"].widget.attrs.update({"class": "form-select"})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ticket_messages"] = self.object.messages.select_related("sender")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # اگه ادمین یه پیام جدید (پاسخ) فرستاده باشه
        reply_message = request.POST.get("reply_message", "").strip()
        if reply_message:
            TicketMessage.objects.create(
                ticket=self.object,
                sender=request.user,
                message=reply_message,
                is_staff_reply=True,
            )
            messages.success(request, _("پاسخ شما ثبت شد."))

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "dashboard:admin:ticket_update", kwargs={"pk": self.object.pk}
        )


class TicketDeleteView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    model = Ticket
    template_name = "dashboard/admin/tickets/ticket-delete.html"
    success_url = reverse_lazy("dashboard:admin:ticket_list")
    success_message = _("تیکت با موفقیت حذف شد")
