from .models import ActivityLog

def log_activity(user, action_type, description, group=None):
    """
    Creates an activity record in the database.
    """
    return ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        group=group
    )
