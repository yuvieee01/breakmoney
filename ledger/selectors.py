from decimal import Decimal
from django.db.models import Sum
from expenses.models import ExpenseParticipant, Expense
from settlements.models import Settlement

def get_user_net_balance(user, group=None):
    """
    Calculates the absolute net balance for a user.
    Positive means they are owed money. Negative means they owe money.
    """
    participants = ExpenseParticipant.objects.filter(user=user)
    if group:
        participants = participants.filter(expense__group=group)
        
    exp_paid = participants.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
    exp_owed = participants.aggregate(total=Sum('amount_owed'))['total'] or Decimal('0.00')
    expense_net = exp_paid - exp_owed

    settlements_paid = Settlement.objects.filter(payer=user)
    settlements_received = Settlement.objects.filter(receiver=user)
    
    if group:
        settlements_paid = settlements_paid.filter(group=group)
        settlements_received = settlements_received.filter(group=group)
        
    settled_paid = settlements_paid.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    settled_received = settlements_received.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    settlement_net = settled_paid - settled_received

    return (expense_net + settlement_net).quantize(Decimal('0.01'))

def get_all_user_balances(group=None):
    """
    Returns a dictionary of {user_object: Decimal_balance} for everyone.
    Strictly groups by user.id to prevent fragmented balances.
    """
    balances_by_id = {}
    users_map = {}
    
    # 1. Aggregate Expenses
    expenses = Expense.objects.all()
    if group:
        expenses = expenses.filter(group=group)
        
    for p in ExpenseParticipant.objects.filter(expense__in=expenses).select_related('user'):
        uid = p.user.id
        if uid not in balances_by_id:
            balances_by_id[uid] = Decimal('0.00')
            users_map[uid] = p.user
        balances_by_id[uid] += (p.amount_paid - p.amount_owed)

    # 2. Aggregate Settlements
    settlements = Settlement.objects.all()
    if group:
        settlements = settlements.filter(group=group)
        
    for s in settlements.select_related('payer', 'receiver'):
        pid = s.payer.id
        rid = s.receiver.id
        
        if pid not in balances_by_id:
            balances_by_id[pid] = Decimal('0.00')
            users_map[pid] = s.payer
        if rid not in balances_by_id:
            balances_by_id[rid] = Decimal('0.00')
            users_map[rid] = s.receiver
            
        balances_by_id[pid] += s.amount
        balances_by_id[rid] -= s.amount

    # Return final mapped dictionary
    final_balances = {}
    for uid, bal in balances_by_id.items():
        if bal != Decimal('0.00'):
            final_balances[users_map[uid]] = bal.quantize(Decimal('0.01'))
            
    return final_balances