from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from . import services

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        return email

    def save(self, commit=True):
        """
        Use the service layer so later side-effects live in services.py.
        """
        data = self.cleaned_data
        password = data.get("password1")

        user = services.create_user(
            email=data["email"],
            password=password,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        )

        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "timezone", "email_notifications")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "timezone", "email_notifications")
        help_texts = {
            "timezone": "Your local timezone (e.g. UTC, Asia/Kolkata)"
        }

    def save(self, commit=True):
        if commit:
            return services.update_user_profile(self.instance, **self.cleaned_data)
        return super().save(commit=False)


class ResendVerificationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()