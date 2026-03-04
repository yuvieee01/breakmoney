from decimal import Decimal
from . import selectors

def simplify_debts(group=None):
    """
    The core Splitwise algorithm.
    Takes all balances and simplifies them into the minimum number of transactions.
    """
    balances = selectors.get_all_user_balances(group=group)
    
    debtors = []   # People who owe money (balance < 0)
    creditors = [] # People who are owed money (balance > 0)

    for user, balance in balances.items():
        if balance < Decimal('-0.001'):
            debtors.append([user, abs(balance)])
        elif balance > Decimal('0.001'):
            creditors.append([user, balance])

    # Sort largest debts first for optimal reduction
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    raw_transactions = []
    i = 0
    j = 0

    while i < len(debtors) and j < len(creditors):
        debtor_user, debt_amount = debtors[i]
        creditor_user, credit_amount = creditors[j]

        # The amount to settle is the smaller of the two
        settle_amount = min(debt_amount, credit_amount)
        
        raw_transactions.append({
            'from_user': debtor_user,
            'to_user': creditor_user,
            'amount': settle_amount.quantize(Decimal('0.01'))
        })

        # Update remaining balances
        debtors[i][1] -= settle_amount
        creditors[j][1] -= settle_amount

        # Move to next person if fully settled
        if debtors[i][1] < Decimal('0.001'):
            i += 1
        if creditors[j][1] < Decimal('0.001'):
            j += 1

    # --- FOOLPROOF MERGE ---
    # Strictly combine any accidental duplicate paths before returning to the UI
    merged_transactions = {}
    for t in raw_transactions:
        # Use a unique tuple of IDs as the key (e.g., User 1 paying User 2)
        key = (t['from_user'].id, t['to_user'].id)
        
        if key not in merged_transactions:
            merged_transactions[key] = {
                'from_user': t['from_user'],
                'to_user': t['to_user'],
                'amount': t['amount']
            }
        else:
            # If a duplicate line exists, just mathematically add the amounts together!
            merged_transactions[key]['amount'] += t['amount']

    return list(merged_transactions.values())

def get_dashboard_summary(user):
    """
    Runs the simplify algorithm globally and extracts the stats for a specific user.
    """
    all_transactions = simplify_debts(group=None)
    
    you_owe_list = [t for t in all_transactions if t['from_user'] == user]
    you_are_owed_list = [t for t in all_transactions if t['to_user'] == user]
    
    total_you_owe = sum(t['amount'] for t in you_owe_list) or Decimal('0.00')
    total_you_are_owed = sum(t['amount'] for t in you_are_owed_list) or Decimal('0.00')
    net_total = total_you_are_owed - total_you_owe

    return {
        'net_balance': net_total,
        'total_owed': total_you_owe,
        'total_to_receive': total_you_are_owed,
        'you_owe_list': you_owe_list,
        'you_are_owed_list': you_are_owed_list
    }