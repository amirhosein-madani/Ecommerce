from django.contrib import admin
from website.models import Newsletter, ContactUs, Wishlist, TicketMessage, Ticket

# Register your models here.


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ["email", "created_at"]
    search_fields = ["email"]


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "subject", "is_read", "created_at"]
    list_filter = ["is_read"]
    readonly_fields = ["full_name", "email", "subject", "message", "created_at"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "product_count", "updated_at"]
    search_fields = ["user__username", "user__email"]
    filter_horizontal = ["products"]
    readonly_fields = ["updated_at"]

    def product_count(self, obj):
        return obj.products.count()


class TicketMessageInline(admin.TabularInline):
    """Show a ticket's messages inline on the Ticket admin page,
    so staff can read and reply to the conversation without leaving
    the ticket detail view.
    """

    model = TicketMessage
    extra = 1
    fields = ["sender", "message", "is_staff_reply", "created_at"]
    readonly_fields = ["created_at"]
    ordering = ["created_at"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "subject",
        "user",
        "category",
        "priority",
        "status",
        "order",
        "created_at",
        "closed_at",
    ]
    list_filter = ["status", "category", "priority", "created_at"]
    search_fields = ["subject", "user__username", "user__email", "id"]
    autocomplete_fields = ["user", "order"]
    readonly_fields = ["created_at", "updated_at", "closed_at"]
    ordering = ["-created_at"]
    inlines = [TicketMessageInline]

    fieldsets = (
        (None, {"fields": ("user", "subject", "order")}),
        ("Classification", {"fields": ("category", "priority", "status")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "closed_at")}),
    )


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    """Registered standalone as well, for searching/filtering messages
    across all tickets (e.g. finding all staff replies) without having
    to open each ticket individually.
    """

    list_display = ["id", "ticket", "sender", "is_staff_reply", "created_at"]
    list_filter = ["is_staff_reply", "created_at"]
    search_fields = ["message", "sender__username", "ticket__subject"]
    autocomplete_fields = ["ticket", "sender"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
