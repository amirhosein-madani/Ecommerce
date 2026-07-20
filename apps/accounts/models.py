from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from .validators import (
    phone_validator,
    username_validator,
    validate_national_code,
)

# post_save   post_delete pre_save pre_delete4


class UserType(models.IntegerChoices):
    CUSTOMER = 1, _("Customer")
    ADMIN = 2, _("Admin")
    SUPERUSER = 3, _("Superuser")


class UserManager(BaseUserManager):
    def create_user(
        self,
        username,
        email,
        national_code,
        password=None,
    ):
        """
        Creates and saves a regular user.
        """

        if not username:
            raise ValueError("Users must have a username.")

        if not national_code:
            raise ValueError("Users must have a national code.")

        user = self.model(
            username=username,
            email=email,
            national_code=national_code,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        email,
        national_code,
        password,
    ):
        """
        Creates and saves a superuser.
        """

        user = self.create_user(
            username=username,
            email=email,
            national_code=national_code,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.user_type = UserType.SUPERUSER
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    custom user model
    """

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator, MinLengthValidator(4)],
    )
    national_code = models.CharField(
        max_length=10,
        unique=True,
        validators=[validate_national_code],
    )
    user_type = models.IntegerField(choices=UserType.choices, default=UserType.CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "national_code"]

    def __str__(self):
        return self.username


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        unique=True,
        validators=[phone_validator],
    )
    date_of_birth = models.DateField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture",
        default="default/avatar.png",
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}"


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, pk=instance.pk)
