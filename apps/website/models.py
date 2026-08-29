from django.db import models
from django.urls import reverse

# Create your models here.


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse("website:newsletter-detail", kwargs={"pk": self.pk})

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
