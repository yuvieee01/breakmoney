from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from . import services

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'timezone', 'email_notifications')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'timezone', 'email_notifications')
        help_texts = {
            'timezone': 'Your local timezone (e.g. UTC, Asia/Kolkata)'
        }

    def save(self, commit=True):
        if commit:
            return services.update_user_profile(self.instance, **self.cleaned_data)
        return super().save(commit=False)