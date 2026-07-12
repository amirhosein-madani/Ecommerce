from django.contrib import admin
from website.models import Newsletter, ContactUs

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
