from django import forms
from website.models import Newsletter, ContactUs


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["email"]

        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ایمیل خود را وارد کنید",
                }
            ),
        }


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ["full_name", "email", "subject", "message"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "نام و نام خانوادگی",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "email@site.com",
                    "dir": "ltr",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "موضوع مورد نظر را وارد نمایید",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "توضیحات خود را وارد نمایید",
                    "rows": 4,
                }
            ),
        }
