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
    user = User.objects.create_user(email=email, password=password, **extra_fields)
    return user


@transaction.atomic
def update_user_profile(user: User, **data) -> User:
    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    user.save()
    return user


def build_absolute_url(request, path: str) -> str:
    if request is not None:
        return request.build_absolute_uri(path)

    site_url = getattr(settings, "SITE_URL", "") or getattr(settings, "DJANGO_SITE_URL", "")
    site_url = (site_url or "").rstrip("/")
    return f"{site_url}{path}"


@transaction.atomic
def send_verification_email(user: User, request=None) -> None:
    EmailVerificationToken.objects.filter(user=user, used_at__isnull=True).delete()

    token_obj, raw_token = EmailVerificationToken.create_for_user(user)

    verify_path = reverse("accounts:verify_email", kwargs={"token": raw_token})
    verify_url = build_absolute_url(request, verify_path)

    ttl_hours = int(getattr(settings, "EMAIL_VERIFICATION_TOKEN_TTL_HOURS", 24))

    subject = "Verify your Breakmoney email"
    message = (
        f"Hi {user.get_full_name() or user.email},\n\n"
        f"Thanks for signing up for Breakmoney.\n\n"
        f"Please verify your email by clicking this link:\n"
        f"{verify_url}\n\n"
        f"This link expires in {ttl_hours} hours.\n\n"
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
def verify_email_token(raw_token: str) -> tuple[bool, str, User | None]:
    if not raw_token:
        return False, "Invalid verification link.", None

    token_hash = EmailVerificationToken.hash_token(raw_token)

    try:
        token_obj = EmailVerificationToken.objects.select_related("user").get(token_hash=token_hash)
    except EmailVerificationToken.DoesNotExist:
        return False, "Invalid verification link.", None

    if token_obj.is_used:
        if getattr(token_obj.user, "email_verified", False):
            return True, "Your email is already verified.", token_obj.user
        return False, "This verification link has already been used.", None

    if token_obj.is_expired:
        return False, "This verification link has expired. Please request a new one.", None

    user = token_obj.user
    user.email_verified = True
    if hasattr(user, "email_verified_at"):
        user.email_verified_at = timezone.now()
        user.save(update_fields=["email_verified", "email_verified_at"])
    else:
        user.save(update_fields=["email_verified"])

    token_obj.mark_used()
    return True, "Email verified successfully. Logging you in…", user