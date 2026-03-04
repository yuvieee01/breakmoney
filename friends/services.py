from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from .models import Friendship, FriendInvitation
from . import selectors

User = get_user_model()

@transaction.atomic
def add_friend_by_email(current_user, email: str):
    """
    Business logic: 
    If user exists -> Link immediately.
    If not -> Create a pending invite and send an email.
    """
    email = email.lower().strip()
    
    if current_user.email.lower() == email:
        raise ValueError("You cannot add yourself as a friend.")

    target_user = User.objects.filter(email=email).first()

    if target_user:
        if selectors.are_friends(current_user, target_user):
            raise ValueError(f"You are already friends with {email}.")
        
        # Sort users by ID to prevent duplicate A->B and B->A rows in the database
        u1, u2 = sorted([current_user, target_user], key=lambda u: u.id)
        friendship = Friendship.objects.create(user1=u1, user2=u2)
        return friendship, "FRIEND_ADDED"
        
    else:
        if FriendInvitation.objects.filter(sender=current_user, email=email, status='PENDING').exists():
             raise ValueError(f"An invitation to {email} is already pending.")
             
        invitation = FriendInvitation.objects.create(sender=current_user, email=email)
        
        # In Development, this will print to your terminal console
        send_mail(
            subject=f"{current_user.get_full_name() or current_user.email} invited you to Breakmoney",
            message=f"Join Breakmoney to easily split expenses!",
            from_email="noreply@breakmoney.com",
            recipient_list=[email],
            fail_silently=True,
        )
        return invitation, "INVITE_SENT"

@transaction.atomic
def remove_friend(current_user, target_user):
    """Soft/Hard remove a friend connection."""
    u1, u2 = sorted([current_user, target_user], key=lambda u: u.id)
    # For now, we hard delete the friendship. 
    # (If balances != 0, we'll enforce that rule in the views later)
    Friendship.objects.filter(user1=u1, user2=u2).delete()