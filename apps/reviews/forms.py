# reviews/forms.py
from django import forms
from reviews.models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["description", "rate"]
        widgets = {
            "rate": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }
