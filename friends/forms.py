from django import forms

class AddFriendForm(forms.Form):
    email = forms.EmailField(
        label="Friend's Email address",
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email address'})
    )