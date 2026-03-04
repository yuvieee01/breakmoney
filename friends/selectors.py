from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Friendship, FriendInvitation

User = get_user_model()

def get_user_friends(user):
    """Return a QuerySet of User objects who are friends with the given user."""
    # Find all friendship records where the user is either user1 or user2
    friendships = Friendship.objects.filter(Q(user1=user) | Q(user2=user))
    
    # Extract the IDs of the *other* person in each friendship
    friend_ids = []
    for f in friendships:
        if f.user1_id == user.id:
            friend_ids.append(f.user2_id)
        else:
            friend_ids.append(f.user1_id)
            
    return User.objects.filter(id__in=friend_ids).order_by('first_name', 'email')

def are_friends(user1, user2) -> bool:
    """Check if two users are already friends."""
    u1, u2 = sorted([user1, user2], key=lambda u: u.id)
    return Friendship.objects.filter(user1=u1, user2=u2).exists()

def get_pending_invites_for_user(user):
    """Return all pending email invitations sent by the user."""
    return FriendInvitation.objects.filter(sender=user, status='PENDING').order_by('-created_at')