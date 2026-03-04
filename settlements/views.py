from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SettleForm
from . import services

@login_required
def create_settlement_view(request):
    initial_data = {}
    
    payer_id = request.GET.get('payer_id')
    receiver_id = request.GET.get('receiver_id')
    group_id = request.GET.get('group_id')
    amount_val = request.GET.get('amount') # NEW: Grab the amount from URL
    
    if receiver_id: initial_data['receiver'] = receiver_id
    if payer_id: initial_data['payer'] = payer_id
    if not payer_id: initial_data['payer'] = request.user.id
    if group_id: initial_data['group'] = group_id
    if amount_val: initial_data['amount'] = amount_val # NEW: Set initial amount

    if request.method == 'POST':
        form = SettleForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                settlement = services.create_settlement(
                    payer=form.cleaned_data['payer'],
                    receiver=form.cleaned_data['receiver'],
                    amount=form.cleaned_data['amount'],
                    date=form.cleaned_data['date'],
                    group=form.cleaned_data['group'],
                    notes=form.cleaned_data['notes']
                )
                messages.success(request, f"Successfully recorded payment of ₹{settlement.amount} from {settlement.payer.first_name} to {settlement.receiver.first_name}.")
                if settlement.group:
                    return redirect('groups:detail', group_id=settlement.group.id)
                return redirect('ledger:dashboard')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = SettleForm(user=request.user, initial=initial_data)

    return render(request, 'settlements/settle_form.html', {'form': form})

@login_required
def delete_settlement_view(request, settlement_id):
    if request.method == 'POST':
        try:
            services.delete_settlement(settlement_id, request.user)
            messages.success(request, "Settlement deleted. Balances have been restored.")
        except PermissionError as e:
            messages.error(request, str(e))
    return redirect('ledger:dashboard')