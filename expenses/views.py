from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense
from .forms import ExpenseForm
from . import services, selectors
from groups.selectors import get_group_with_members, get_group_members
from friends.selectors import get_user_friends
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def expense_detail_view(request, expense_id):
    expense = selectors.get_expense_details(expense_id)
    if not expense:
        messages.error(request, "Expense not found.")
        return redirect('ledger:dashboard')
    return render(request, 'expenses/expense_detail.html', {'expense': expense})

@login_required
def expense_create_view(request):
    friends = get_user_friends(request.user)
    friend_id_param = request.GET.get('friend_id')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        payer_choice = request.POST.get('payer')
        split_with_id = request.POST.get('split_with')
        
        if form.is_valid() and payer_choice and split_with_id:
            try:
                friend_user = User.objects.get(id=split_with_id)
                if friend_user not in friends:
                    raise ValueError("You can only add direct expenses with your friends.")
                
                amount = form.cleaned_data['amount']
                split_type = form.cleaned_data['split_type']
                
                payer_id = request.user.id if payer_choice == 'me' else friend_user.id
                
                participants_data = []
                # Me
                amt_paid_me = amount if payer_id == request.user.id else Decimal('0.00')
                weight_me = Decimal('1.0') if split_type == 'EQUAL' else Decimal(request.POST.get('split_value_me', '0') or '0')
                participants_data.append({'user': request.user, 'amount_paid': amt_paid_me, 'weight': weight_me})
                
                # Them
                amt_paid_them = amount if payer_id == friend_user.id else Decimal('0.00')
                weight_them = Decimal('1.0') if split_type == 'EQUAL' else Decimal(request.POST.get('split_value_them', '0') or '0')
                participants_data.append({'user': friend_user, 'amount_paid': amt_paid_them, 'weight': weight_them})
                
                expense = services.create_expense(
                    user=request.user, group=None, description=form.cleaned_data['description'],
                    amount=amount, date=form.cleaned_data['date'], category=form.cleaned_data['category'],
                    split_type=split_type, participants_data=participants_data, notes=form.cleaned_data['notes'],
                    receipt=form.cleaned_data.get('receipt')
                )
                
                messages.success(request, f"Added expense: {expense.description}")
                return redirect('ledger:dashboard')
                
            except (ValueError, InvalidOperation, User.DoesNotExist) as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form_individual.html', {
        'form': form, 
        'friends': friends,
        'selected_friend_id': int(friend_id_param) if friend_id_param and friend_id_param.isdigit() else None
    })

@login_required
def group_expense_create_view(request, group_id):
    group = get_group_with_members(group_id, request.user)
    if not group:
        messages.error(request, "Group not found.")
        return redirect('groups:list')

    members = [m.user for m in get_group_members(group)]

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        payer_id = request.POST.get('payer')
        
        if form.is_valid() and payer_id:
            try:
                amount = form.cleaned_data['amount']
                split_type = form.cleaned_data['split_type']
                
                participants_data = []
                for user in members:
                    amt_paid = amount if str(user.id) == payer_id else Decimal('0.00')
                    # Extract dynamic split values from POST based on member ID
                    if split_type == 'EQUAL':
                        weight_val = Decimal('1.0')
                    else:
                        raw_weight = request.POST.get(f'split_value_{user.id}', '0')
                        weight_val = Decimal(raw_weight if raw_weight.strip() else '0')
                        
                    participants_data.append({'user': user, 'amount_paid': amt_paid, 'weight': weight_val})
                
                expense = services.create_expense(
                    user=request.user, group=group, description=form.cleaned_data['description'],
                    amount=amount, date=form.cleaned_data['date'], category=form.cleaned_data['category'],
                    split_type=split_type, participants_data=participants_data, notes=form.cleaned_data['notes'],
                    receipt=form.cleaned_data.get('receipt')
                )
                
                messages.success(request, f"Added expense: {expense.description}")
                return redirect('groups:detail', group_id=group.id)
                
            except (ValueError, InvalidOperation) as e:
                messages.error(request, f"Error calculating splits: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below and ensure a payer is selected.")
    else:
        form = ExpenseForm()

    return render(request, 'expenses/expense_form.html', {'form': form, 'group': group, 'members': members})

@login_required
def expense_delete_view(request, expense_id):
    if request.method == 'POST':
        try:
            expense = get_object_or_404(Expense, id=expense_id)
            group_id = expense.group_id
            services.delete_expense(expense_id, request.user)
            messages.success(request, "Expense deleted successfully. Balances have been restored.")
            if group_id:
                return redirect('groups:detail', group_id=group_id)
            return redirect('ledger:dashboard')
        except PermissionError as e:
            messages.error(request, str(e))
    return redirect('expenses:detail', expense_id=expense_id)