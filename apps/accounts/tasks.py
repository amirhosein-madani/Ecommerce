from celery import shared_task
from templated_email import send_templated_mail


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
