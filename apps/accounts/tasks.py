import logging
from celery import shared_task
from templated_email import send_templated_mail
from accounts.models import PasswordResetToken, EmailVerificationToken
from django.utils import timezone
from datetime import timedelta
from django.db import models

logger = logging.getLogger(__name__)


@shared_task
def send_reset_password_email(email, username, uid, token):
    send_templated_mail(
        template_name="reset-password",
        from_email="noreply@example.com",
        recipient_list=[email],
        context={
            "username": username,
            "uidb64": uid,
            "token": token,
            "site_name": "My Shop",
            "domain": "http://localhost:8000",
        },
    )


@shared_task
def send_welcome_email(username, email):
    send_templated_mail(
        template_name="welcome",
        from_email="noreply@example.com",
        recipient_list=[email],
        context={
            "username": username,
            "email": email,
            "site_name": "My Shop",
            "domain": "http://localhost:8000",
        },
    )


@shared_task
def registration_email(email, username, token):
    send_templated_mail(
        template_name="test-email",
        from_email="noreply@example.com",
        recipient_list=[email],
        context={
            "username": username,
            "site_name": "localhost",
            "verification_token": (token),
        },
    )


@shared_task
def reset_password_email(email, username, token):
    send_templated_mail(
        template_name="reset-password",
        from_email="noreply@example.com",
        recipient_list=[email],
        context={
            "username": username,
            "site_name": "localhost",
            "token": token,
            "expiry_minutes": 15,
        },
    )


@shared_task
def delete_expired_verification_tokens():
    expiry_threshold = timezone.now() - timedelta(minutes=15)

    deleted_count, _ = EmailVerificationToken.objects.filter(
        models.Q(is_used=True) | models.Q(created_at__lt=expiry_threshold)
    ).delete()

    logger.info("Deleted %d expired/used verification tokens", deleted_count)


@shared_task
def delete_expired_reset_password_tokens():

    expiry_threshold = timezone.now() - timedelta(minutes=15)

    deleted_count, _ = PasswordResetToken.objects.filter(
        models.Q(is_used=True) | models.Q(created_at__lt=expiry_threshold)
    ).delete()

    logger.info("Deleted %d expired/used reset-password tokens", deleted_count)
