from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class Payment(models.Model):
    order = models.OneToOneField(
        "order.Order",
        on_delete=models.PROTECT,
        related_name="payment",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    authority = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
    )

    ref_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Payment #{self.pk} - {self.status}"
