
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _


class AdminPasswordChangeForm(PasswordChangeForm):

    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": _("رمز عبور فعلی وارد شده اشتباه است."),
        "password_mismatch": _("رمز عبور جدید و تکرار آن با هم مطابقت ندارند."),
    }

    old_password = forms.CharField(
        label="رمز عبور فعلی",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "currentPasswordLabel",
                "autocomplete": "current-password",
            }
        ),
    )
    new_password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "newPassword",
                "autocomplete": "new-password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="تایید رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "confirmNewPasswordLabel",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean(self):

        cleaned_data = super().clean()

        new_password1 = cleaned_data.get("new_password1")

        if new_password1 and self.user.check_password(new_password1):
            self.add_error(
                "new_password1",
                _("رمز عبور جدید نباید با رمز عبور قبلی یکسان باشد."),
            )

        return cleaned_data
