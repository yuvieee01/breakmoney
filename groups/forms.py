from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AddMemberForm(forms.Form):
    email = forms.EmailField(
        label="User's Email address",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter registered email'})
    )