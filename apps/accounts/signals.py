import django.dispatch
from django.dispatch import receiver
from accounts.tasks import send_welcome_email

user_login_notification = django.dispatch.Signal()


@receiver(user_login_notification)
def send_login_email(sender, user, request, **kwargs):

    if not user.email:
        return

    send_welcome_email.delay(user.username, user.email)
