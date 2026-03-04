from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

@transaction.atomic
def create_user(email: str, password: str = None, **extra_fields) -> User:
    """
    Service to handle user creation logic.
    Ensures any side effects (like creating default ledgers later) happen here.
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