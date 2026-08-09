from django import forms

from order.models.orders import UserAddress


class UserAddressForm(forms.ModelForm):

    class Meta:
        model = UserAddress

        fields = [
            "address_name",
            "address",
            "state",
            "city",
            "zip_code",
        ]

        widgets = {
            "address_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "اسم آدرس",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "استان",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "شهر",
                }
            ),
            "zip_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "کد پستی",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "آدرس کامل",
                    "rows": 4,
                }
            ),
        }
