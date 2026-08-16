from django.db import models
from django.utils import timezone
from products.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class Coupon(models.Model):

    code = models.CharField(
        max_length=30,
        unique=True,
    )

    discount = models.PositiveIntegerField(default=0)

    minimum_order_price = models.PositiveIntegerField(
        default=0,
    )

    max_discount = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="coupons",
    )

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="coupons",
    )

    max_usage = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    @property
    def usage_count(self):
        return self.usages.count()

    def save(self, *args, **kwargs):
        if self.expires_at and timezone.now() >= self.expires_at:
            self.is_active = False

        if self.max_usage is not None:
            usage_count = self.usages.count()

            if usage_count >= self.max_usage:
                self.is_active = False

        super().save(*args, **kwargs)


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "coupon"],
                name="unique_user_coupon",
            )
        ]
