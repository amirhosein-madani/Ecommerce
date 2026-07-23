from django import forms
from products.models import Product
from ckeditor.widgets import CKEditorWidget


class ProductUpdateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "brief_description",
            "category",
            "price",
            "status",
            "discount_percent",
            "stock",
            "image",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Product title",
                }
            ),
            "description": CKEditorWidget(
                attrs={
                    "class": "form-control",
                }
            ),
            "brief_description": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "category": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "discount_percent": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "image",
        ]
