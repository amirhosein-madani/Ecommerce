from django.core.management.base import BaseCommand
from faker import Faker
from website.models import Newsletter


class Command(BaseCommand):
    help = "generate random Newsletter"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):

        for _ in range(10):
            Newsletter.objects.create(email=self.fake.email())
