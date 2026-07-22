from django.views.generic import UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Profile
from dashboard.permissions import HasCustomerAccessPermission
from dashboard.forms import ProfileEditForm, ProfileImageEditForm


class CustomerProfileEditView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, UpdateView
):

    template_name = "dashboard/customer/profile/profile-edit.html"
    form_class = ProfileEditForm
    success_url = reverse_lazy("dashboard:customer:profile_edit")
    success_message = _(" پورفایل با موفقیت تغییر کرد")

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class ProfileImageEditView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)
        form = ProfileImageEditForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, _("تصویر پروفایل با موفقیت به‌روزرسانی شد"))
        else:
            messages.error(request, _("فایل انتخاب‌شده معتبر نیست"))

        return redirect("dashboard:customer:profile_edit")


class ProfileImageDeleteView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)

        default_image = profile._meta.get_field("profile_picture").default

        if profile.profile_picture and profile.profile_picture.name != default_image:
            profile.profile_picture.delete(save=False)

        profile.profile_picture = default_image
        profile.save()

        messages.success(request, _("تصویر پروفایل به حالت پیش‌فرض بازگشت"))
        return redirect("dashboard:customer:profile_edit")
