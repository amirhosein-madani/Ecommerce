from django.core.management.base import BaseCommand
from faker import Faker
from products.models import Category


class Command(BaseCommand):
    help = "generate random categories"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):

        for _ in range(10):
            Category.objects.create(
                name=self.fake.word(),
                is_active=True,
            )
