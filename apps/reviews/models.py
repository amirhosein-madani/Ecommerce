from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Status(models.TextChoices):
    PENDING = "pending", _("در انتظار تایید")
    APPROVED = "approved", _("تایید شده")
    REJECTED = "rejected", _("رد شده")


class Review(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("User")
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Product"),
    )
    description = models.TextField(verbose_name=_("Description"))
    rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_("Rate")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product_review"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rate}/5)"
