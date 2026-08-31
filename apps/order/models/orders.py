from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product

User = get_user_model()


class OrderStatusType(models.IntegerChoices):

    PENDING = 1, _("در انتظار پرداخت")
    PAID = 2, _("پرداخت شده")
    PROCESSING = 3, _("در حال پردازش")
    SHIPPED = 4, _("ارسال شده")
    DELIVERED = 5, _("تحویل داده شده")
    CANCELED = 6, _("لغو شده")


class UserAddress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="addresses",
    )
    address_name = models.CharField(
        null=True,
        max_length=50,
    )

    address = models.CharField(max_length=250, null=True)

    state = models.CharField(max_length=50, null=True)

    city = models.CharField(max_length=50, null=True)

    zip_code = models.CharField(max_length=10, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.city}"


class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.PositiveSmallIntegerField(
        choices=OrderStatusType.choices,
        default=OrderStatusType.PENDING,
    )

    coupon = models.ForeignKey(
        "Coupon",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
    )

    shipping_address = models.ForeignKey(
        UserAddress, on_delete=models.PROTECT, null=True
    )
    discount_amount = models.PositiveIntegerField(
        default=0,
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"سفارش {self.pk}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
    )
    tax_amount = models.PositiveIntegerField(blank=True, null=True)

    @property
    def total_price(self):

        if self.price is None or self.quantity is None:
            return 0

        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"
