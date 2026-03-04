from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Group, GroupMember
from . import selectors

User = get_user_model()

@transaction.atomic
def create_group(name: str, creator: User, description: str = '', icon=None):
    group = Group.objects.create(
        name=name,
        created_by=creator,
        description=description,
        icon=icon
    )
    GroupMember.objects.create(group=group, user=creator, role='ADMIN')
    return group

@transaction.atomic
def add_member_by_email(group, request_user, email: str, role: str = 'MEMBER'):
    # We removed the Admin check here so ANY current member can invite others!
    
    email = email.lower().strip()
    target_user = User.objects.filter(email=email).first()

    if not target_user:
        raise ValueError(f"No user found with email {email}. They must register first.")

    if GroupMember.objects.filter(group=group, user=target_user).exists():
        raise ValueError(f"{target_user.get_full_name()} is already in this group.")

    member = GroupMember.objects.create(group=group, user=target_user, role=role)
    return member

@transaction.atomic
def remove_member(group, request_user, target_user_id: int):
    # Only Admins can remove people
    if not selectors.is_group_admin(group, request_user):
         raise PermissionError("Only group admins can remove members.")
         
    target_membership = GroupMember.objects.filter(group=group, user_id=target_user_id).first()
    if not target_membership:
        raise ValueError("User is not in this group.")

    if target_membership.role == 'ADMIN':
        admin_count = GroupMember.objects.filter(group=group, role='ADMIN').count()
        if admin_count <= 1:
             raise ValueError("Cannot remove the last admin of the group.")

    target_membership.delete()

@transaction.atomic
def delete_group(group, request_user):
    # Only Admins can delete the entire group
    if not selectors.is_group_admin(group, request_user):
        raise PermissionError("Only group admins can delete the group.")
    
    # Deleting the group will cascade and delete all associated Expenses and Settlements
    group.delete()