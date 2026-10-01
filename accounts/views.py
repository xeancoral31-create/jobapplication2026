"""accounts/views.py — Auth views: login, logout, signup, password reset, role redirect."""
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import render, redirect
from django.views import View

from .forms import (
    EmailAuthenticationForm,
    SignupForm,
    InkboardPasswordResetForm,
    ApplicantProfileForm,
)

User = get_user_model()


# ── Helpers ────────────────────────────────────────────────────────────────

def _role_redirect_url(user) -> str:
    """Return the landing URL for a given user's role."""
    if user.role == User.Role.EMPLOYER:
        return "/employer/"
    if user.role == User.Role.ADMIN or user.is_staff:
        return "/admin-panel/"
    return "/applicant/"


# ── Role redirect (used as LOGIN_REDIRECT_URL destination) ─────────────────

def role_redirect(request):
    """Redirect to the correct role dashboard immediately after login."""
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    return redirect(_role_redirect_url(request.user))


# ── Login ──────────────────────────────────────────────────────────────────

from django.core.cache import cache
from django.http import HttpResponse

LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutes


def _get_rate_limit_key(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR", "127.0.0.1")
    return f"login_attempts_{ip}"


def _is_rate_limited(request):
    key = _get_rate_limit_key(request)
    return cache.get(key, 0) >= LOGIN_ATTEMPTS_LIMIT


def _record_failed_login(request):
    key = _get_rate_limit_key(request)
    current = cache.get(key, 0) + 1
    cache.set(key, current, timeout=LOGIN_ATTEMPTS_TIMEOUT)
    return current


def _reset_login_rate_limit(request):
    key = _get_rate_limit_key(request)
    cache.delete(key)


class LoginView(View):
    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(_role_redirect_url(request.user))
        return render(request, self.template_name, {"form": self.form_class(request)})

    def post(self, request):
        if _is_rate_limited(request):
            return HttpResponse(
                "Too many login attempts. Please wait 5 minutes before trying again.",
                status=429,
                content_type="text/plain",
            )

        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            _reset_login_rate_limit(request)
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next") or _role_redirect_url(user)
            return redirect(next_url)

        _record_failed_login(request)
        # Suspended message is surfaced via form error; also add a flash for visibility
        if form.errors.get("__all__") and "suspended" in str(form.errors):
            messages.error(
                request,
                "Your account has been suspended. Contact support@inkboard.dev.",
            )
        return render(request, self.template_name, {"form": form})


# ── Admin login (plum accent, /admin-login/) ───────────────────────────────

class AdminLoginView(View):
    template_name = "accounts/admin_login.html"
    form_class = EmailAuthenticationForm

    def get(self, request):
        if request.user.is_authenticated and (
            request.user.role == User.Role.ADMIN or request.user.is_staff
        ):
            return redirect("/admin-panel/")
        return render(request, self.template_name, {"form": self.form_class(request)})

    def post(self, request):
        if _is_rate_limited(request):
            return HttpResponse(
                "Too many login attempts. Please wait 5 minutes before trying again.",
                status=429,
                content_type="text/plain",
            )

        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            _reset_login_rate_limit(request)
            user = form.get_user()
            if user.role != User.Role.ADMIN and not user.is_staff:
                messages.error(request, "Admin access only. Use the standard login page.")
                return render(request, self.template_name, {"form": form})
            login(request, user)
            return redirect("/admin-panel/")

        _record_failed_login(request)
        return render(request, self.template_name, {"form": form})


# ── Logout ─────────────────────────────────────────────────────────────────

class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect("/")

    # Allow GET as well (e.g. clicking a link)
    def get(self, request):
        logout(request)
        return redirect("/")


# ── Signup ─────────────────────────────────────────────────────────────────

class SignupView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(_role_redirect_url(request.user))
        role = request.GET.get("role", "applicant")
        form = SignupForm(initial={"role": role})
        return render(request, self.template_name, {"form": form, "initial_role": role})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend="accounts.backends.EmailBackend",
            )
            if user.role == User.Role.EMPLOYER:
                messages.success(
                    request,
                    "Account created! Your employer profile is pending approval — "
                    "you'll be notified once activated.",
                )
                return redirect("/employer/pending/")
            messages.success(request, "Welcome to Inkboard! Start exploring jobs below.")
            return redirect("/applicant/")
        role = request.POST.get("role", "applicant")
        return render(request, self.template_name, {"form": form, "initial_role": role})


# ── Password reset (use Django built-ins with custom templates/form) ────────

class InkboardPasswordResetView(PasswordResetView):
    form_class = InkboardPasswordResetForm
    template_name = "registration/password_reset.html"
    email_template_name = "registration/password_reset_email.txt"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = "/accounts/password-reset/done/"


class InkboardPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class InkboardPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = "/accounts/password-reset/complete/"


class InkboardPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


# ── Profile Management ──────────────────────────────────────────────────────

@login_required
def profile_view(request):
    """View and update applicant profile (full_name, phone, location, resume)."""
    if request.user.role != User.Role.APPLICANT:
        messages.info(request, "Employer profiles are managed via the employer dashboard.")
        return redirect("core:employer_dashboard")

    if request.method == "POST":
        form = ApplicantProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ApplicantProfileForm(user=request.user)

    has_resume = bool(
        hasattr(request.user, "applicant_profile") and request.user.applicant_profile.resume
    )
    resume_file = (
        request.user.applicant_profile.resume if has_resume else None
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "has_resume": has_resume,
            "resume_file": resume_file,
        },
    )

