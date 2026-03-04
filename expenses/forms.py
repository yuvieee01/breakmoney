from django import forms
from django.utils import timezone
from .models import Expense

class ExpenseForm(forms.ModelForm):
    """Base form for the Expense details."""
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)
    
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'date', 'category', 'split_type', 'notes', 'receipt']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

# Because expense participant logic is highly dynamic (adding/removing users, varying amounts),
# it is usually handled in Django via Formsets or custom JS in the template passing JSON.
# We will use standard POST dictionary parsing in the View for maximum flexibility with Bootstrap.
