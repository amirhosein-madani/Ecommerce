from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Wishlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )
    products = models.ManyToManyField(
        "products.Product",
        related_name="wishlisted_by",
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
