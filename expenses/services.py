from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from .models import Expense, ExpenseParticipant

def _calculate_splits(amount: Decimal, split_type: str, participants_data: list) -> list:
    total_participants = len(participants_data)
    if total_participants == 0:
        return participants_data

    amount = amount.quantize(Decimal('0.01'))
    
    if split_type == 'EXACT':
        total_exact = sum(Decimal(str(p['weight'])) for p in participants_data)
        if total_exact != amount:
            raise ValueError(f"Exact amounts sum (₹{total_exact}) must equal total amount (₹{amount}).")
        for p in participants_data:
            p['amount_owed'] = Decimal(str(p['weight'])).quantize(Decimal('0.01'))
        return participants_data

    elif split_type == 'EQUAL':
        base_share = (amount / Decimal(total_participants)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        for p in participants_data:
            p['amount_owed'] = base_share
        remainder = amount - (base_share * total_participants)

    elif split_type == 'PERCENTAGE':
        total_pct = sum(Decimal(str(p['weight'])) for p in participants_data)
        if total_pct != Decimal('100'):
            raise ValueError("Percentages must sum exactly to 100.")
            
        distributed = Decimal('0.00')
        for p in participants_data:
            pct = Decimal(str(p['weight']))
            share = ((amount * pct) / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            p['amount_owed'] = share
            distributed += share
        remainder = amount - distributed

    elif split_type == 'SHARES':
        total_shares = sum(Decimal(str(p['weight'])) for p in participants_data)
        if total_shares <= 0:
            raise ValueError("Total shares must be greater than 0.")
            
        distributed = Decimal('0.00')
        for p in participants_data:
            shares = Decimal(str(p['weight']))
            share = ((amount * shares) / total_shares).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            p['amount_owed'] = share
            distributed += share
        remainder = amount - distributed
        
    elif split_type == 'ADJUSTMENT':
        total_adj = sum(Decimal(str(p['weight'])) for p in participants_data)
        base_amount = amount - total_adj
        base_share = (base_amount / Decimal(total_participants)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        
        distributed = Decimal('0.00')
        for p in participants_data:
            share = base_share + Decimal(str(p['weight']))
            p['amount_owed'] = share
            distributed += share
        remainder = amount - distributed
    else:
        raise ValueError("Invalid split type.")

    # Distribute pennies
    remainder = remainder.quantize(Decimal('0.01'))
    penny = Decimal('0.01')
    sorted_p = sorted(participants_data, key=lambda x: (-Decimal(str(x.get('amount_paid', 0))), x['user'].id))
    
    idx = 0
    while remainder > Decimal('0.00'):
        sorted_p[idx]['amount_owed'] += penny
        remainder -= penny
        idx = (idx + 1) % total_participants

    return participants_data

@transaction.atomic
def create_expense(user, group, description, amount, date, category, split_type, participants_data, notes='', receipt=None):
    amount = Decimal(str(amount)).quantize(Decimal('0.01'))
    total_paid = sum(Decimal(str(p.get('amount_paid', 0))) for p in participants_data)
    if total_paid != amount:
        raise ValueError(f"Total paid (₹{total_paid}) does not match expense amount (₹{amount}).")

    calculated_participants = _calculate_splits(amount, split_type, participants_data)

    expense = Expense.objects.create(
        group=group, description=description, amount=amount, date=date,
        category=category, split_type=split_type, notes=notes, receipt=receipt, created_by=user
    )

    for p_data in calculated_participants:
        ExpenseParticipant.objects.create(
            expense=expense, user=p_data['user'],
            amount_paid=Decimal(str(p_data.get('amount_paid', 0))),
            amount_owed=p_data['amount_owed'],
            weight=Decimal(str(p_data.get('weight', 0)))
        )
    return expense

@transaction.atomic
def delete_expense(expense_id, request_user):
    expense = Expense.objects.get(id=expense_id)
    if not expense.participants.filter(user=request_user).exists() and expense.created_by != request_user:
        raise PermissionError("You do not have permission to delete this expense.")
    expense.delete()