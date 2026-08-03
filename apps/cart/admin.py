from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("display_total_price",)
    fields = ("product", "quantity", "price", "display_total_price")
    autocomplete_fields = ("product",)

    @admin.display(description="جمع")
    def display_total_price(self, obj):
        if obj.pk is None:
            return "—"
        return obj.total_price


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "item_count",
        "total_price",
        "created_at",
        "updated_at",
    )
    list_select_related = ("user",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]

    @admin.display(description="تعداد اقلام")
    def item_count(self, obj):
        return obj.items.count()

    @admin.display(description="جمع کل")
    def total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "price", "total_price")
    list_select_related = ("cart", "cart__user", "product")
    search_fields = ("cart__user__username", "product__title")
    autocomplete_fields = ("cart", "product")
