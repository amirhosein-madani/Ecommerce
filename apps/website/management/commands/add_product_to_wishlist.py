from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User

from products.models import Product, ProductStatusType
from random import choice
from website.models.wishlists import Wishlist


class Command(BaseCommand):
    help = "add product to wishlist"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        products = list(Product.objects.filter(status=ProductStatusType.PUBLISH))

        user = User.objects.get(email="amirmadani901@gmail.com")

        for _ in range(10):
            wishlist = Wishlist.objects.get(user=user)

            product = choice(products)
            wishlist.products.add(product)

        self.stdout.write(self.style.SUCCESS("wishlist updated successfully."))
