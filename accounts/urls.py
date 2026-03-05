from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="accounts:login"), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),

    path("verification-sent/", views.VerificationSentView.as_view(), name="verification_sent"),
    path("verify-email/<uuid:token>/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("resend-verification/", views.ResendVerificationView.as_view(), name="resend_verification"),
]