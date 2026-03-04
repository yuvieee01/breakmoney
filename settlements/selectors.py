from django.db.models import Q
from .models import Settlement

def get_user_settlements(user):
    """Fetch all settlements where the user is either the payer or receiver."""
    return Settlement.objects.filter(Q(payer=user) | Q(receiver=user)).order_by('-date', '-created_at')

def get_group_settlements(group):
    """Fetch all settlements tied to a specific group."""
    return Settlement.objects.filter(group=group).order_by('-date', '-created_at')

def get_settlements_between_users(user1, user2):
    """Fetch all settlements between two specific users."""
    return Settlement.objects.filter(
        (Q(payer=user1) & Q(receiver=user2)) | (Q(payer=user2) & Q(receiver=user1))
    ).order_by('-date', '-created_at')
