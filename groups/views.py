from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import GroupForm, AddMemberForm
from . import selectors, services
from ledger.selectors import get_user_net_balance
from ledger import services as ledger_services

@login_required
def group_list_view(request):
    groups = list(selectors.get_user_groups(request.user))
    
    for group in groups:
        group.balance = get_user_net_balance(request.user, group=group)
        
    return render(request, 'groups/group_list.html', {'groups': groups})

@login_required
def group_create_view(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = services.create_group(
                name=form.cleaned_data['name'],
                creator=request.user,
                description=form.cleaned_data['description'],
                icon=form.cleaned_data.get('icon')
            )
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('groups:detail', group_id=group.id)
    else:
        form = GroupForm()
        
    return render(request, 'groups/group_form.html', {'form': form})

@login_required
def group_detail_view(request, group_id):
    group = selectors.get_group_with_members(group_id, request.user)
    if not group:
        messages.error(request, "Group not found or you don't have access.")
        return redirect('groups:list')

    members = selectors.get_group_members(group)
    is_admin = selectors.is_group_admin(group, request.user)
    
    add_member_form = AddMemberForm() 

    if request.method == 'POST' and 'add_member' in request.POST:
        add_member_form = AddMemberForm(request.POST)
        if add_member_form.is_valid():
            try:
                services.add_member_by_email(group=group, request_user=request.user, email=add_member_form.cleaned_data['email'])
                messages.success(request, "Member added successfully.")
                return redirect('groups:detail', group_id=group.id)
            except (ValueError, PermissionError) as e:
                messages.error(request, str(e))

    group_balance = get_user_net_balance(request.user, group=group)
    
    # Fetch and explicitly order expenses by newest date, then exact creation time
    expenses = group.expenses.all().order_by('-date', '-created_at')

    context = {
        'group': group,
        'members': members,
        'is_admin': is_admin,
        'add_member_form': add_member_form,
        'group_balance': group_balance,
        'expenses': expenses
    }
    return render(request, 'groups/group_detail.html', context)

@login_required
def group_balances_view(request, group_id):
    """New view to show exactly who owes who within a specific group."""
    group = selectors.get_group_with_members(group_id, request.user)
    if not group:
        messages.error(request, "Group not found or you don't have access.")
        return redirect('groups:list')

    # Run the simplification algorithm strictly for this group
    transactions = ledger_services.simplify_debts(group=group)
    
    return render(request, 'groups/group_balances.html', {
        'group': group,
        'transactions': transactions
    })

@login_required
def group_remove_member_view(request, group_id, user_id):
    if request.method == 'POST':
        group = selectors.get_group_with_members(group_id, request.user)
        if group:
            try:
                services.remove_member(group, request.user, user_id)
                messages.success(request, "Member removed from group.")
            except (ValueError, PermissionError) as e:
                messages.error(request, str(e))
    return redirect('groups:detail', group_id=group_id)

@login_required
def group_delete_view(request, group_id):
    if request.method == 'POST':
        group = selectors.get_group_with_members(group_id, request.user)
        if group:
            try:
                services.delete_group(group, request.user)
                messages.success(request, f"Group '{group.name}' was successfully deleted.")
                return redirect('groups:list')
            except PermissionError as e:
                messages.error(request, str(e))
    return redirect('groups:detail', group_id=group_id)