from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        # Superusers should be verified by default
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("email_verified_at", timezone.now())

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # Remove username field entirely
    email = models.EmailField(_("email address"), unique=True)

    # Custom Profile fields
    default_currency = models.CharField(max_length=3, default="USD")
    timezone = models.CharField(max_length=63, default="UTC")
    email_notifications = models.BooleanField(default=True)

    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = super().get_full_name()
        return full_name if full_name else self.email


class EmailVerificationToken(models.Model):
    """
    One-time token for verifying email ownership.

    - token: random UUID (unguessable)
    - expires_at: TTL enforced
    - used_at: one-time use
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["used_at"]),
        ]

    def is_used(self) -> bool:
        return self.used_at is not None

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def mark_used(self):
        if not self.used_at:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])

    def __str__(self):
        return f"EmailVerificationToken(user={self.user_id}, token={self.token})"