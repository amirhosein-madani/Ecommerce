from django import forms

from order.models.orders import UserAddress


class CheckOutForm(forms.Form):

    address_id = forms.IntegerField(
        required=True,
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        address_id = cleaned_data.get("address_id")

        if address_id:
            address = UserAddress.objects.filter(
                id=address_id,
                user=self.user,
            ).first()

            if not address:
                raise forms.ValidationError("این آدرس متعلق به شما نیست.")

        return cleaned_data
