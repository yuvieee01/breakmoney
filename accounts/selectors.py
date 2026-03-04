from django.core.exceptions import ObjectDoesNotExist
from .models import User

def get_user_by_email(email: str) -> User | None:
    """Fetch a user by their email address."""
    try:
        return User.objects.get(email=email)
    except ObjectDoesNotExist:
        return None

def get_active_users():
    """Return all active users."""
    return User.objects.filter(is_active=True)