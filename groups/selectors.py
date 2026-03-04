from django.core.exceptions import ObjectDoesNotExist
from .models import Group, GroupMember

def get_user_groups(user):
    """Return a QuerySet of all groups a user belongs to."""
    return Group.objects.filter(memberships__user=user).order_by('-created_at')

def get_group_with_members(group_id, user):
    """
    Fetch a group and verify the user is a member. 
    Returns the Group object or raises an exception.
    """
    try:
        group = Group.objects.get(id=group_id)
        # Security check: User must be in the group to view it
        if not GroupMember.objects.filter(group=group, user=user).exists():
            return None
        return group
    except ObjectDoesNotExist:
        return None

def get_group_members(group):
    """Return all members of a specific group."""
    return GroupMember.objects.filter(group=group).select_related('user')

def is_group_admin(group, user):
    """Check if a specific user has Admin privileges in a group."""
    return GroupMember.objects.filter(group=group, user=user, role='ADMIN').exists()