"""accounts/views.py — Auth views: login, logout, signup, password reset, role redirect."""
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from .email_service import (
    EMAILJS_PUBLIC_KEY,
    EMAILJS_SERVICE_ID,
    EMAILJS_TEMPLATE_PRIMARY,
    EMAILJS_TEMPLATE_SECONDARY,
    generate_verification_code,
    send_verification_email,
)
from .forms import (
    ApplicantProfileForm,
    EmailAuthenticationForm,
    PasswordResetChangePasswordForm,
    PasswordResetVerifyForm,
    SignupForm,
    WorkWisePasswordResetForm,
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


# ── Login Rate Limiting ───────────────────────────────────────────────────

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
        if form.errors.get("__all__") and "suspended" in str(form.errors):
            messages.error(
                request,
                "Your account has been suspended. Contact support@workwise.dev.",
            )
        return render(request, self.template_name, {"form": form})


# ── Logout ─────────────────────────────────────────────────────────────────

class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect("/")

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
            messages.success(request, "Welcome to WorkWise! Start exploring jobs below.")
            return redirect("/applicant/")
        role = request.POST.get("role", "applicant")
        return render(request, self.template_name, {"form": form, "initial_role": role})


# ── Password Reset Session Helpers ─────────────────────────────────────────

def _clean_reset_session(request):
    """Remove password reset session artifacts."""
    for key in [
        "reset_user_id",
        "reset_email",
        "reset_code",
        "reset_code_expires",
        "reset_attempts",
        "reset_verified",
        "emailjs_payload",
    ]:
        request.session.pop(key, None)


# ── Password Reset Flow ────────────────────────────────────────────────────

class WorkWisePasswordResetView(View):
    """Step 1: Request verification code to registered email."""
    template_name = "registration/password_reset.html"
    form_class = WorkWisePasswordResetForm

    def get(self, request):
        form = self.form_class()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "emailjs_service_id": EMAILJS_SERVICE_ID,
                "emailjs_public_key": EMAILJS_PUBLIC_KEY,
                "emailjs_template_id": EMAILJS_TEMPLATE_PRIMARY,
                "emailjs_template_secondary": EMAILJS_TEMPLATE_SECONDARY,
            },
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                user = None

            if user and not user.is_suspended:
                code = generate_verification_code()
                request.session["reset_user_id"] = user.id
                request.session["reset_email"] = user.email
                request.session["reset_code"] = code
                request.session["reset_code_expires"] = time.time() + 900  # 15 mins
                request.session["reset_attempts"] = 0
                request.session["reset_verified"] = False

                # Dispatch via backend and get payload for browser EmailJS SDK
                email_payload = send_verification_email(user, code)
                request.session["emailjs_payload"] = email_payload

                if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
                    return JsonResponse({
                        "success": True,
                        "email": user.email,
                        "redirect_url": "/accounts/password-reset/verify/",
                        "emailjs": email_payload,
                    })

                messages.success(
                    request,
                    f"A 6-digit verification code has been sent to {user.email}. Please check your inbox.",
                )
                return redirect("accounts:password_reset_verify")
            elif user and user.is_suspended:
                form.add_error(
                    "email",
                    "This account has been suspended. Please contact support@workwise.dev.",
                )
            else:
                form.add_error(
                    "email",
                    "No registered account was found with this email address.",
                )

        if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
            errors = [err for errlist in form.errors.values() for err in errlist]
            return JsonResponse({"success": False, "errors": errors}, status=400)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "emailjs_service_id": EMAILJS_SERVICE_ID,
                "emailjs_public_key": EMAILJS_PUBLIC_KEY,
                "emailjs_template_id": EMAILJS_TEMPLATE_PRIMARY,
                "emailjs_template_secondary": EMAILJS_TEMPLATE_SECONDARY,
            },
        )


class PasswordResetResendView(View):
    """AJAX / POST endpoint to re-generate and resend verification code."""

    def post(self, request):
        user_id = request.session.get("reset_user_id")
        if not user_id:
            return JsonResponse(
                {"success": False, "error": "No active reset session. Please enter your email again."},
                status=400,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Account not found."}, status=404)

        code = generate_verification_code()
        request.session["reset_code"] = code
        request.session["reset_code_expires"] = time.time() + 900
        request.session["reset_attempts"] = 0
        request.session["reset_verified"] = False

        email_payload = send_verification_email(user, code)
        request.session["emailjs_payload"] = email_payload

        return JsonResponse({
            "success": True,
            "message": f"A new verification code has been sent to {user.email}.",
            "emailjs": email_payload,
        })


class PasswordResetVerifyView(View):
    """Step 2: Enter & validate 6-digit verification code, show confirmation prompt."""
    template_name = "registration/password_reset_verify.html"
    form_class = PasswordResetVerifyForm

    def get(self, request):
        email = request.session.get("reset_email")
        user_id = request.session.get("reset_user_id")
        if not email or not user_id:
            messages.warning(request, "Please enter your email to request a verification code.")
            return redirect("accounts:password_reset")

        form = self.form_class()
        emailjs_payload = request.session.get("emailjs_payload")
        verified = request.session.get("reset_verified", False)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "email": email,
                "emailjs_payload": emailjs_payload,
                "verified": verified,
                "emailjs_service_id": EMAILJS_SERVICE_ID,
                "emailjs_public_key": EMAILJS_PUBLIC_KEY,
            },
        )

    def post(self, request):
        user_id = request.session.get("reset_user_id")
        email = request.session.get("reset_email")
        saved_code = request.session.get("reset_code")
        expires = request.session.get("reset_code_expires", 0)
        attempts = request.session.get("reset_attempts", 0)

        if not user_id or not saved_code:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": "Session expired. Please request a new code."}, status=400)
            messages.error(request, "Session expired. Please request a new code.")
            return redirect("accounts:password_reset")

        form = self.form_class(request.POST)

        if time.time() > expires:
            form.add_error("code", "Verification code has expired. Please click 'Resend Code'.")
        elif attempts >= 5:
            form.add_error("code", "Too many invalid attempts. Please request a fresh verification code.")
        elif form.is_valid():
            entered_code = form.cleaned_data["code"]
            if entered_code == str(saved_code).strip():
                # Verification success!
                request.session["reset_verified"] = True
                if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
                    return JsonResponse({
                        "success": True,
                        "verified": True,
                        "message": "Verification code verified successfully!",
                    })
                return render(
                    request,
                    self.template_name,
                    {
                        "form": form,
                        "email": email,
                        "verified": True,
                        "prompt_dialog": True,
                    },
                )
            else:
                request.session["reset_attempts"] = attempts + 1
                form.add_error("code", "Invalid verification code. Please check your email and try again.")

        if request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", ""):
            errors = [err for errlist in form.errors.values() for err in errlist]
            return JsonResponse({"success": False, "errors": errors}, status=400)

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "email": email,
                "verified": False,
            },
        )


class PasswordResetDecisionView(View):
    """
    Handles prompt response to: “Do you want to change your password?”
    - 'yes': Navigates to dedicated password-change page
    - 'no': Keeps current password unchanged & immediately redirects to dashboard
    """

    def post(self, request):
        user_id = request.session.get("reset_user_id")
        verified = request.session.get("reset_verified", False)

        if not user_id or not verified:
            messages.warning(request, "Please verify your email code first.")
            return redirect("accounts:password_reset")

        decision = request.POST.get("decision", "").strip().lower()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            _clean_reset_session(request)
            return redirect("accounts:login")

        if decision == "no":
            # Keep existing password unchanged, log in user, and redirect to their account dashboard
            login(request, user, backend="accounts.backends.EmailBackend")
            _clean_reset_session(request)
            messages.info(request, "Your password was kept unchanged. Welcome back to your dashboard!")
            return redirect(_role_redirect_url(user))

        elif decision == "yes":
            # Proceed to dedicated password-change page
            return redirect("accounts:password_reset_change")

        # Fallback if invalid post
        return redirect("accounts:password_reset_verify")


class PasswordResetChangeView(View):
    """Step 3: Dedicated password-change page where user enters & confirms new password."""
    template_name = "registration/password_reset_change.html"
    form_class = PasswordResetChangePasswordForm

    def get(self, request):
        user_id = request.session.get("reset_user_id")
        verified = request.session.get("reset_verified", False)

        if not user_id or not verified:
            messages.warning(request, "Please verify your verification code first.")
            return redirect("accounts:password_reset")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            _clean_reset_session(request)
            return redirect("accounts:login")

        form = self.form_class(user=user)
        return render(request, self.template_name, {"form": form, "user_obj": user})

    def post(self, request):
        user_id = request.session.get("reset_user_id")
        verified = request.session.get("reset_verified", False)

        if not user_id or not verified:
            messages.warning(request, "Session expired. Please request a new verification code.")
            return redirect("accounts:password_reset")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            _clean_reset_session(request)
            return redirect("accounts:login")

        form = self.form_class(request.POST, user=user)
        if form.is_valid():
            user = form.save()
            # Log the user into their account with the updated credentials
            login(request, user, backend="accounts.backends.EmailBackend")
            _clean_reset_session(request)
            messages.success(
                request,
                "Your password has been successfully updated! This is now your permanent password.",
            )
            return redirect(_role_redirect_url(user))

        return render(request, self.template_name, {"form": form, "user_obj": user})


class PasswordChangeSettingView(View):
    """Allows logged-in users to update their password from account settings."""
    template_name = "accounts/change_password.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        form = PasswordChangeForm(user=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect("accounts:profile")
        return render(request, self.template_name, {"form": form})


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
