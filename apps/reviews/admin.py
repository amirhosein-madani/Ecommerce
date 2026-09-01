# reviews/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rate", "status", "created_at")
    list_filter = ("status", "rate", "created_at")
    search_fields = ("user__username", "user__email", "product__title", "description")
    list_editable = ("status",)
    autocomplete_fields = ("user", "product")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 30

    actions = ["approve_reviews", "reject_reviews"]

    @admin.action(description=_("Approve selected reviews"))
    def approve_reviews(self, request, queryset):
        updated = queryset.update(status=Review.Status.APPROVED)
        self.message_user(request, _(f"{updated} review(s) approved."))

    @admin.action(description=_("Reject selected reviews"))
    def reject_reviews(self, request, queryset):
        updated = queryset.update(status=Review.Status.REJECTED)
        self.message_user(request, _(f"{updated} review(s) rejected."))
