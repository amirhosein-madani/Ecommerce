from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models.functions import Round


class ProductStatusType(models.IntegerChoices):
    """
    Product status choices.
    """

    PUBLISH = 1, _("فعال")
    DRAFT = 2, _("غیر فعال")


class ProductQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=ProductStatusType.PUBLISH)

    def sort(self, sort_by):
        if sort_by == "-created_at":
            return self.order_by("-created_at")

        if sort_by == "created_at":
            return self.order_by("created_at")

        if sort_by == "-price":
            return self.order_by("-annotated_final_price")

        if sort_by == "price":
            return self.order_by("annotated_final_price")

        return self

    def with_final_price(self):
        return self.annotate(
            annotated_final_price=Round(
                ExpressionWrapper(
                    F("price") - (F("price") * F("discount_percent") / Decimal("100")),
                    output_field=DecimalField(
                        max_digits=10,
                        decimal_places=2,
                    ),
                )
            )
        )


class Product(models.Model):
    """
    this is ProductModel
    """

    objects = ProductQuerySet.as_manager()
    title = models.CharField(max_length=50)
    description = models.TextField()
    brief_description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField("Category", related_name="products")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField(
        default="default/product-image.png", upload_to="product/img/"
    )
    status = models.IntegerField(
        choices=ProductStatusType.choices,
        default=ProductStatusType.DRAFT,
    )
    slug = models.SlugField(blank=True, unique=True, allow_unicode=True)
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    stock = models.PositiveIntegerField(default=0)
    is_discounted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.is_discounted = self.discount_percent > 0
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product:product_detail", kwargs={"slug": self.slug})

    @property
    def final_price(self):
        discount_amount = self.price * (Decimal(self.discount_percent) / Decimal("100"))
        return round(self.price - discount_amount)

    @property
    def is_published(self):
        return self.status == ProductStatusType.PUBLISH

    @property
    def is_available(self):
        return self.stock > 0

    class Meta:
        ordering = ["-created_at"]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="product/extra-images/")


class Category(models.Model):
    """
    this is a model for ProdcutModel's category
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True)
    image = models.ImageField(upload_to="product_categories", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product:category_detail", kwargs={"slug": self.slug})

    class Meta:
        verbose_name_plural = "Categories"
