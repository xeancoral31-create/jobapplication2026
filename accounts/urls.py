"""accounts/urls.py"""
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # ── Auth ───────────────────────────────────────────────────────────────
    path("login/",   views.LoginView.as_view(),  name="login"),
    path("logout/",  views.LogoutView.as_view(), name="logout"),
    path("register/", views.SignupView.as_view(), name="register"),
    path("redirect/", views.role_redirect,        name="role_redirect"),
    path("profile/", views.profile_view,          name="profile"),

    # ── Password reset & verification flow ──────────────────────────────────
    path("password-reset/",
         views.WorkWisePasswordResetView.as_view(),
         name="password_reset"),
    path("password-reset/resend/",
         views.PasswordResetResendView.as_view(),
         name="password_reset_resend"),
    path("password-reset/verify/",
         views.PasswordResetVerifyView.as_view(),
         name="password_reset_verify"),
    path("password-reset/decision/",
         views.PasswordResetDecisionView.as_view(),
         name="password_reset_decision"),
    path("password-reset/change/",
         views.PasswordResetChangeView.as_view(),
         name="password_reset_change"),
    path("change-password/",
         views.PasswordChangeSettingView.as_view(),
         name="change_password"),
]
