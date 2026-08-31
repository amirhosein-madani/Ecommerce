from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
User = get_user_model()


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ["-created_at"]


class ContactUs(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} -- {self.subject}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Contact us"


class TicketStatus(models.TextChoices):
    OPEN = "open", _("باز")
    IN_PROGRESS = "in_progress", _("در حال بررسی")
    ANSWERED = "answered", _("پاسخ داده شده")
    CLOSED = "closed", _("بسته شده")


class TicketCategory(models.TextChoices):
    ORDER = "order", _("سفارش")
    PAYMENT = "payment", _("پرداخت")
    PRODUCT = "product", _("محصول")
    ACCOUNT = "account", _("حساب کاربری")
    TECHNICAL = "technical", _("فنی")
    OTHER = "other", _("سایر")


class TicketPriority(models.TextChoices):
    LOW = "low", _("کم")
    MEDIUM = "medium", _("متوسط")
    HIGH = "high", _("بالا")
    URGENT = "urgent", _("فوری")


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )
    subject = models.CharField(max_length=50)
    status = models.CharField(choices=TicketStatus.choices, default=TicketStatus.OPEN)
    category = models.CharField(
        choices=TicketCategory.choices, default=TicketCategory.OTHER
    )
    priority = models.CharField(
        choices=TicketPriority.choices, default=TicketPriority.MEDIUM
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} - {self.subject}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ticket_messages",
    )
    message = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message on Ticket #{self.ticket_id}"
