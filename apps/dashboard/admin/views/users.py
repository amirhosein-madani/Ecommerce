from django.views.generic import DeleteView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from dashboard.permissions import HasAdminAccessPermission
from accounts.models import User, UserType


class UserListView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    ListView,
):

    template_name = "dashboard/admin/users/user-list.html"
    paginate_by = 10

    def get_queryset(self):

        queryset = User.objects.all()

        # -----------------------------
        # Search
        # -----------------------------

        search_q = self.request.GET.get("q")

        if search_q:
            queryset = queryset.filter(username__icontains=search_q)

        # -----------------------------
        # Status Filter
        # -----------------------------

        status = self.request.GET.get("status")

        if status in UserType.values:
            queryset = queryset.filter(status=status)

        # -----------------------------
        # Ordering
        # -----------------------------

        order_by = self.request.GET.get("order_by")

        if order_by in [
            "created_at",
            "-created_at",
        ]:
            queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["total_items"] = self.object_list.count()
        context["status_types"] = UserType.choices

        return context

    # -----------------------------
    # Pagination
    # -----------------------------

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


class UserUpdateView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    UpdateView,
):
    model = User
    template_name = "dashboard/admin/users/user-edit.html"
    fields = ["email", "user_type", "is_active", "is_verified"]
    success_url = reverse_lazy("dashboard:admin:user_list")
    success_message = _("اطلاعات کاربر با موفقیت ویرایش شد.")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["email"].widget.attrs.update({"class": "form-control"})
        form.fields["user_type"].widget.attrs.update({"class": "form-select"})
        form.fields["is_active"].widget.attrs.update({"class": "form-check-input"})
        form.fields["is_verified"].widget.attrs.update({"class": "form-check-input"})
        return form


class UserDeleteView(
    LoginRequiredMixin,
    HasAdminAccessPermission,
    SuccessMessageMixin,
    DeleteView,
):
    model = User
    template_name = "dashboard/admin/users/user-delete.html"
    success_url = reverse_lazy("dashboard:admin:user_list")
    success_message = _("کاربر با موفقیت حذف شد")
