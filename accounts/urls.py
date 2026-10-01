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

    # ── Password reset chain ────────────────────────────────────────────────
    path("password-reset/",
         views.InkboardPasswordResetView.as_view(),
         name="password_reset"),
    path("password-reset/done/",
         views.InkboardPasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/",
         views.InkboardPasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("password-reset/complete/",
         views.InkboardPasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
]
