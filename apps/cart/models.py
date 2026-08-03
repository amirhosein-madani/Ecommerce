from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        unique_together = ["cart", "product"]

    @property
    def total_price(self):
        if self.price is None or self.quantity is None:
            return None
        return self.price * self.quantity

    def __str__(self):
        return f"{self.cart.user.username} - {self.product.title} ({self.quantity})"
