from decimal import Decimal
from django.db import transaction
from .models import Settlement

@transaction.atomic
def create_settlement(payer, receiver, amount, date, group=None, notes=''):
    amount = Decimal(str(amount)).quantize(Decimal('0.01'))
    
    if payer == receiver:
        raise ValueError("You cannot settle a debt with yourself.")
    if amount <= Decimal('0.00'):
        raise ValueError("Settlement amount must be greater than zero.")

    settlement = Settlement.objects.create(
        payer=payer, receiver=receiver, group=group,
        amount=amount, date=date, notes=notes
    )
    return settlement

@transaction.atomic
def delete_settlement(settlement_id, request_user):
    settlement = Settlement.objects.get(id=settlement_id)
    if request_user not in [settlement.payer, settlement.receiver]:
        raise PermissionError("Only the payer or receiver can delete this settlement.")
    settlement.delete()