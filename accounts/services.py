from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .models import EmailVerificationToken

User = get_user_model()


@transaction.atomic
def create_user(email: str, password: str = None, **extra_fields) -> User:
    """
    Service to handle user creation logic.
    """
    user = User.objects.create_user(email=email, password=password, **extra_fields)
    return user


@transaction.atomic
def update_user_profile(user: User, **data) -> User:
    """
    Service to update a user's profile settings.
    """
    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    user.save()
    return user


@transaction.atomic
def create_email_verification_token(user: User) -> EmailVerificationToken:
    """
    Create a new verification token (valid for N hours).
    We also optionally invalidate old unused tokens (cleaner + safer).
    """
    ttl_hours = getattr(settings, "EMAIL_VERIFICATION_TOKEN_TTL_HOURS", 24)
    expires_at = timezone.now() + timezone.timedelta(hours=ttl_hours)

    # Invalidate previous unused tokens (optional but tidy)
    EmailVerificationToken.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())

    return EmailVerificationToken.objects.create(user=user, expires_at=expires_at)


def build_absolute_url(request, path: str) -> str:
    """
    Build absolute URL in a proxy-safe way.
    Uses request if available, else SITE_URL.
    """
    if request is not None:
        return request.build_absolute_uri(path)

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    return f"{site_url}{path}"


def send_verification_email(user: User, request=None) -> None:
    """
    Sends verification link to the user's email.
    """
    token_obj = create_email_verification_token(user)
    verify_path = reverse("accounts:verify_email", kwargs={"token": str(token_obj.token)})
    verify_url = build_absolute_url(request, verify_path)

    subject = "Verify your Breakmoney email"
    message = (
        f"Hi {user.get_full_name() or user.email},\n\n"
        f"Thanks for signing up for Breakmoney.\n\n"
        f"Please verify your email by clicking this link:\n"
        f"{verify_url}\n\n"
        f"This link expires in {getattr(settings, 'EMAIL_VERIFICATION_TOKEN_TTL_HOURS', 24)} hours.\n\n"
        f"If you didn't create this account, you can ignore this email.\n"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[user.email],
        fail_silently=False,
    )


@transaction.atomic
def verify_email_token(token: str) -> tuple[bool, str]:
    """
    Validate token; if valid, verify the user and mark token as used.

    Returns: (success, message)
    """
    try:
        token_obj = EmailVerificationToken.objects.select_related("user").get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return False, "Invalid verification link."

    if token_obj.is_used():
        # If already verified, this is fine: show friendly message.
        if token_obj.user.email_verified:
            return True, "Your email is already verified."
        return False, "This verification link has already been used."

    if token_obj.is_expired():
        return False, "This verification link has expired. Please request a new one."

    user = token_obj.user
    user.email_verified = True
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified", "email_verified_at"])

    token_obj.mark_used()
    return True, "Email verified successfully."