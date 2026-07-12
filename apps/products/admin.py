from django.contrib import admin

from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "stock", "status", "is_discounted")
    list_filter = ("status", "category", "created_at", "is_discounted")
    search_fields = (
        "title",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_per_page = 20
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_per_page = 20


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
    )
    search_fields = ("product__title",)
    autocomplete_fields = ("product",)
