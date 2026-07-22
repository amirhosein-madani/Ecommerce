from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from dashboard.permissions import HasAdminAccessPermission
from dashboard.admin.forms import AdminPasswordChangeForm


class AdminDashboardHomeView(
    LoginRequiredMixin, HasAdminAccessPermission, TemplateView
):
    template_name = "dashboard/admin/home.html"


class AdminSecurityEditView(
    LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, FormView
):
    template_name = "dashboard/admin/profile/security-edit.html"
    form_class = AdminPasswordChangeForm
    success_url = reverse_lazy("dashboard:admin:security_edit")
    success_message = _("رمز عبور با موفقیت تغییر کرد")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)
