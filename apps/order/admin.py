from django.contrib import admin

from order.models.orders import Order, OrderItem
from order.models.coupons import Coupon, CouponUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("total_price",)

    fields = (
        "product",
        "quantity",
        "price",
        "total_price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "status",
        "coupon",
        "discount_amount",
        "total_price",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "total_price",
    )

    search_fields = (
        "product__title",
        "order__id",
    )

    readonly_fields = ("total_price",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "discount",
        "minimum_order_price",
        "max_discount",
        "is_active",
        "max_usage",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "is_active",
        "expires_at",
        "created_at",
    )

    search_fields = ("code",)

    filter_horizontal = (
        "products",
        "categories",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "coupon",
        "order",
        "used_at",
    )

    list_filter = ("used_at",)

    search_fields = (
        "user__username",
        "user__email",
        "coupon__code",
        "order__id",
    )

    readonly_fields = ("used_at",)

    ordering = ("-used_at",)
