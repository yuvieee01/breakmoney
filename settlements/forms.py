from django import forms
from django.utils import timezone
from .models import Settlement
from django.contrib.auth import get_user_model
from groups.models import Group
from friends.selectors import get_user_friends

User = get_user_model()

class SettleForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)
    payer = forms.ModelChoiceField(queryset=User.objects.none(), empty_label="Select Payer")
    receiver = forms.ModelChoiceField(queryset=User.objects.none(), empty_label="Select Receiver")
    
    class Meta:
        model = Settlement
        fields = ['payer', 'receiver', 'amount', 'group', 'date', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional details (e.g. UPI, Cash)'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Get user and their friends to populate the dropdowns
            friends = list(get_user_friends(user))
            valid_user_ids = [u.id for u in friends] + [user.id]
            users_qs = User.objects.filter(id__in=valid_user_ids).order_by('first_name')
            
            self.fields['payer'].queryset = users_qs
            self.fields['receiver'].queryset = users_qs
            
            self.fields['group'].queryset = Group.objects.filter(memberships__user=user)
            self.fields['group'].required = False
            self.fields['group'].empty_label = "Overall (No specific group)"