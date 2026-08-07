from django.contrib.auth import get_user_model
from django.db import models
from products.models import Product
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class OrderStatusType(models.IntegerChoices):
    PENDING = 1, _("Pending")
    PAID = 2, _("Paid")
    PROCESSING = 3, _("Processing")
    SHIPPED = 4, _("Shipped")
    DELIVERED = 5, _("Delivered")
    CANCELED = 6, _("Canceled")


class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.IntegerField(
        max_length=20,
        choices=OrderStatusType.choices,
        default=OrderStatusType.PENDING,
    )

    coupon = models.ForeignKey(
        "Coupon", on_delete=models.PROTECT, blank=True, null=True
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )

    quantity = models.PositiveIntegerField()

    price = models.PositiveIntegerField()
