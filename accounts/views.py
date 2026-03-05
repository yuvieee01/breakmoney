from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views import generic
from django.utils import timezone

from .forms import CustomUserCreationForm, ProfileUpdateForm, ResendVerificationForm
from .models import User
from . import services


class RegisterView(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:verification_sent")

    def form_valid(self, form):
        user = form.save(commit=True)

        # Ensure new users start unverified
        if not user.email_verified:
            services.send_verification_email(user, request=self.request)

        messages.success(
            self.request,
            "Account created. Please check your email to verify your account before logging in."
        )
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()

        # Block login until verified
        if not getattr(user, "email_verified", False):
            messages.error(self.request, "Please verify your email before logging in.")
            # Don't log them in
            return redirect("accounts:login")

        messages.success(self.request, f"Welcome back, {user.get_full_name()}!")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class VerificationSentView(View):
    def get(self, request):
        return render(request, "accounts/verification_sent.html")


class VerifyEmailView(View):
    def get(self, request, token):
        ok, msg = services.verify_email_token(token)
        if ok:
            messages.success(request, msg)
            return render(request, "accounts/verify_email_result.html", {"success": True})
        else:
            messages.error(request, msg)
            return render(request, "accounts/verify_email_result.html", {"success": False})


class ResendVerificationView(View):
    def get(self, request):
        form = ResendVerificationForm()
        return render(request, "accounts/resend_verification.html", {"form": form})

    def post(self, request):
        form = ResendVerificationForm(request.POST)
        if not form.is_valid():
            return render(request, "accounts/resend_verification.html", {"form": form})

        email = form.cleaned_data["email"]
        user = User.objects.filter(email=email).first()

        # Always respond similarly (avoid user enumeration)
        if user and not user.email_verified:
            services.send_verification_email(user, request=request)

        messages.success(request, "If that email exists and is not verified, a new verification link has been sent.")
        return redirect("accounts:login")