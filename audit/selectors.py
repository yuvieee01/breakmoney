from django.db.models import Q
from .models import ActivityLog
from groups.selectors import get_user_groups

def get_user_activity_feed(user):
    """
    Get all activities initiated by the user OR 
    any activities that happened inside groups the user is a member of.
    """
    user_groups = get_user_groups(user)
    
    return ActivityLog.objects.filter(
        Q(user=user) | Q(group__in=user_groups)
    ).distinct().order_by('-created_at')[:50] # Return the 50 most recent events
