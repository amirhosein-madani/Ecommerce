from django import forms
from website.models.tickets import Ticket
from order.models.orders import OrderStatusType


class NewsletterForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg border-0",
                "placeholder": "ایمیل خود را وارد نمایید",
                "aria-label": "ایمیل خود را وارد کنید",
                "id": "subscribeForm",
            }
        )
    )


class TicketForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "توضیح مشکل یا درخواست خود را بنویسید...",
            }
        ),
        label="پیام",
    )

    class Meta:
        model = Ticket
        fields = ["subject", "category", "priority", "order"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "موضوع تیکت را وارد کنید",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "order": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "subject": "موضوع",
            "category": "دسته‌بندی",
            "priority": "اولویت",
            "order": "سفارش مرتبط",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].required = False

        if user is not None:
            self.fields["order"].queryset = user.orders.filter(
                status=OrderStatusType.PAID
            )

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if not message:
            raise forms.ValidationError("پیام نمی‌تواند خالی باشد.")
        return message
