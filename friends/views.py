from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from .forms import AddFriendForm
from . import services, selectors
from ledger import services as ledger_services
from expenses.models import Expense
from settlements.models import Settlement

User = get_user_model()

@login_required
def friend_list_view(request):
    friends = list(selectors.get_user_friends(request.user))
    pending_invites = selectors.get_pending_invites_for_user(request.user)
    
    summary = ledger_services.get_dashboard_summary(request.user)
    for friend in friends:
        friend.balance = Decimal('0.00')
        for debt in summary['you_owe_list']:
            if debt['to_user'] == friend:
                friend.balance = -debt['amount']
        for credit in summary['you_are_owed_list']:
            if credit['from_user'] == friend:
                friend.balance = credit['amount']
    
    context = {
        'friends': friends,
        'pending_invites': pending_invites
    }
    return render(request, 'friends/friend_list.html', context)

@login_required
def friend_add_view(request):
    if request.method == 'POST':
        form = AddFriendForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                obj, action = services.add_friend_by_email(request.user, email)
                if action == "FRIEND_ADDED":
                    messages.success(request, f"Successfully added {email} as a friend!")
                elif action == "INVITE_SENT":
                    messages.success(request, f"User not found. An invitation was sent to {email}.")
                return redirect('friends:list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = AddFriendForm()
    return render(request, 'friends/friend_invite.html', {'form': form})

@login_required
def friend_remove_view(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    if request.method == 'POST':
        services.remove_friend(request.user, friend)
        messages.success(request, f"Removed {friend.email} from your friends.")
        return redirect('friends:list')
    return redirect('friends:list')

@login_required
def friend_detail_view(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    
    summary = ledger_services.get_dashboard_summary(request.user)
    balance = Decimal('0.00')
    
    for debt in summary['you_owe_list']:
        if debt['to_user'] == friend:
            balance = -debt['amount']
            break
            
    for credit in summary['you_are_owed_list']:
        if credit['from_user'] == friend:
            balance = credit['amount']
            break

    # Using select_related('group') so we can display it nicely in the template
    shared_expenses = Expense.objects.filter(
        participants__user=request.user
    ).filter(
        participants__user=friend
    ).select_related('group', 'created_by').distinct()

    shared_settlements = Settlement.objects.filter(
        Q(payer=request.user, receiver=friend) |
        Q(payer=friend, receiver=request.user)
    ).select_related('group', 'payer', 'receiver')

    history = sorted(
        chain(shared_expenses, shared_settlements),
        key=attrgetter('date', 'created_at'),
        reverse=True
    )
    
    context = {
        'friend': friend,
        'balance': balance,
        'history': history
    }
    return render(request, 'friends/friend_detail.html', context)