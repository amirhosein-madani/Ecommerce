from django import forms
from products.models import Product, ProductImage
from ckeditor.widgets import CKEditorWidget
from order.models.coupons import Coupon


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
        model = ProductImage
        fields = ["image"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class CouponForm(forms.ModelForm):

    class Meta:
        model = Coupon

        fields = [
            "code",
            "discount",
            "minimum_order_price",
            "max_discount",
            "products",
            "categories",
            "max_usage",
            "is_active",
            "expires_at",
        ]

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "کد تخفیف",
                }
            ),
            "discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "درصد تخفیف",
                    "min": 0,
                    "max": 100,
                }
            ),
            "minimum_order_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "حداقل مبلغ سفارش",
                    "min": 0,
                }
            ),
            "max_discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "حداکثر مبلغ تخفیف",
                    "min": 0,
                }
            ),
            "products": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
            "categories": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                }
            ),
            "max_usage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "حداکثر تعداد استفاده",
                    "min": 1,
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "expires_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }
