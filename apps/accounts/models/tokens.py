import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self) -> bool:
        expiry_time = self.created_at + timedelta(minutes=15)
        return not self.is_used and timezone.now() < expiry_time

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reset_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        expiry_time = self.created_at + timedelta(minutes=15)
        return not self.is_used and timezone.now() < expiry_time

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])
