from pathlib import Path
from random import choice
from random import randint
from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker

from products.models import Product, Category, ProductStatusType


class Command(BaseCommand):
    help = "Generate random products"

    def __init__(self):
        super().__init__()
        self.fake = Faker("fa_IR")

    def handle(self, *args, **options):
        categories = list(Category.objects.filter(is_active=True))

        if not categories:
            self.stdout.write(
                self.style.ERROR("No categories found. Create categories first.")
            )
            return

        image_dir = Path(__file__).resolve().parent / "images"
        image_list = list(image_dir.glob("*.jpg"))

        if not image_list:
            self.stdout.write(self.style.ERROR(f"No images found in {image_dir}"))
            return

        for _ in range(10):
            selected_image = choice(image_list)

            product = Product.objects.create(
                title=self.fake.word(),
                description=self.fake.paragraph(nb_sentences=10),
                brief_description=self.fake.sentence(nb_words=10),
                price=self.fake.random_int(min=10000, max=1000000),
                stock=self.fake.random_int(min=0, max=50),
                discount_percent=self.fake.random_int(min=0, max=80),
                status=ProductStatusType.PUBLISH,
            )

            with open(selected_image, "rb") as image_file:
                product.image.save(
                    selected_image.name,
                    File(image_file),
                    save=True,
                )

            product.category.add(choice(categories))

        self.stdout.write(self.style.SUCCESS("Successfully generated 10 products."))
