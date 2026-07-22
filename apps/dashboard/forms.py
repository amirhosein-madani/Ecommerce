from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from accounts.models import Profile


class PasswordChangeForm(PasswordChangeForm):

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


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        exclude = ("user", "created_date", "updated_date", "profile_picture")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام خانوادگی"}
            ),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class ProfileImageEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ("profile_picture",)
