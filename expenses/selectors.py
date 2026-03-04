from .models import Expense, ExpenseParticipant

def get_group_expenses(group):
    """Fetch all expenses associated with a specific group."""
    return Expense.objects.filter(group=group).order_by('-date', '-created_at')

def get_user_expenses(user):
    """Fetch all expenses a user is a participant of."""
    return Expense.objects.filter(participants__user=user).order_by('-date', '-created_at').distinct()

def get_expense_details(expense_id):
    """Fetch expense and eagerly load participants for detail view."""
    try:
        return Expense.objects.prefetch_related('participants__user').get(id=expense_id)
    except Expense.DoesNotExist:
        return None
