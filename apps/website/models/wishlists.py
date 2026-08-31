from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

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


@receiver(post_save, sender=User)
def create_wishlist(sender, instance, created, **kwargs):
    if created:
        Wishlist.objects.create(user=instance)
