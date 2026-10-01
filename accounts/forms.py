"""accounts/forms.py — Signup and login forms."""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import User, EmployerProfile, ApplicantProfile


# ── Email authentication ───────────────────────────────────────────────────


class EmailAuthenticationForm(AuthenticationForm):
    """Override AuthenticationForm to use email instead of username."""

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "placeholder": "you@example.com",
                "class": "form-control",
                "id": "id_email",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "••••••••",
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "suspended": _(
            "Your account has been suspended. Contact support@inkboard.dev."
        ),
    }

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if user.is_suspended:
            raise ValidationError(
                self.error_messages["suspended"],
                code="suspended",
            )
        super().confirm_login_allowed(user)


# ── Public signup ──────────────────────────────────────────────────────────

_FIELD_ATTRS = {"class": "form-control"}


class SignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={**_FIELD_ATTRS, "placeholder": "First name", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={**_FIELD_ATTRS, "placeholder": "Last name", "autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={**_FIELD_ATTRS, "placeholder": "you@domain.com", "autocomplete": "email"}),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={**_FIELD_ATTRS, "placeholder": "Create a password", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        widget=forms.PasswordInput(attrs={**_FIELD_ATTRS, "placeholder": "Confirm your password", "autocomplete": "new-password"}),
    )
    role = forms.ChoiceField(
        choices=[("applicant", "Job Seeker"), ("employer", "Employer")],
        widget=forms.HiddenInput(),
        initial="applicant",
    )
    company_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={**_FIELD_ATTRS, "placeholder": "Your company name"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _("An account with this email already exists. Try logging in instead.")
            )
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1", "")
        p2 = self.cleaned_data.get("password2", "")
        if p1 and p2 and p1 != p2:
            raise ValidationError(_("The two passwords do not match."))
        if len(p1) < 8:
            raise ValidationError(_("Password must be at least 8 characters."))
        return p2

    def clean(self):
        cd = super().clean()
        if cd.get("role") == "employer" and not cd.get("company_name", "").strip():
            first = cd.get("first_name", "").strip()
            last = cd.get("last_name", "").strip()
            cd["company_name"] = f"{first} {last}".strip() or "Hiring Company"
        return cd

    def save(self) -> User:
        """Create User + profile atomically. Returns the new User instance."""
        cd = self.cleaned_data

        with transaction.atomic():
            # Build a unique username from email prefix
            base = cd["email"].split("@")[0].lower()
            username = base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1

            role = cd["role"]
            status = (
                User.Status.PENDING
                if role == User.Role.EMPLOYER
                else User.Status.ACTIVE
            )

            user = User.objects.create_user(
                username=username,
                email=cd["email"],
                password=cd["password1"],
                first_name=cd["first_name"].strip(),
                last_name=cd["last_name"].strip(),
                role=role,
                status=status,
            )

            # Signal already created the profile shell; update company_name for employers
            if role == User.Role.EMPLOYER:
                EmployerProfile.objects.filter(user=user).update(
                    company_name=cd["company_name"].strip()
                )

        return user


# ── Styled password reset form ─────────────────────────────────────────────


class InkboardPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={**_FIELD_ATTRS, "placeholder": "you@example.com", "autocomplete": "email"}
        ),
    )


class ApplicantProfileForm(forms.Form):
    """Profile editing form for applicants to update name, contact, and resume."""

    full_name = forms.CharField(
        label=_("Full Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Jane Doe",
            "autocomplete": "name",
        }),
    )
    phone = forms.CharField(
        label=_("Phone Number"),
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+1 (555) 019-2834",
            "autocomplete": "tel",
        }),
    )
    location = forms.CharField(
        label=_("Location"),
        max_length=120,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "San Francisco, CA or Remote",
        }),
    )
    resume = forms.FileField(
        label=_("Resume / CV"),
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".pdf,.doc,.docx",
        }),
        help_text=_("Upload a PDF or Word document (.pdf, .doc, .docx)."),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        initial = kwargs.get("initial", {})
        if user:
            initial.setdefault("full_name", user.get_full_name() or user.username)
            initial.setdefault("phone", user.phone or "")
            initial.setdefault("location", user.location or "")
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def clean_resume(self):
        from core.validators import validate_resume_file
        resume = self.cleaned_data.get("resume")
        if resume:
            validate_resume_file(resume)
        return resume

    def save(self):
        if not self.user:
            return None
        full_name = self.cleaned_data["full_name"].strip()
        parts = full_name.split(" ", 1)
        self.user.first_name = parts[0]
        self.user.last_name = parts[1] if len(parts) > 1 else ""
        self.user.phone = self.cleaned_data.get("phone", "").strip()
        self.user.location = self.cleaned_data.get("location", "").strip()
        self.user.save(update_fields=["first_name", "last_name", "phone", "location"])

        uploaded_resume = self.cleaned_data.get("resume")
        if uploaded_resume and hasattr(self.user, "applicant_profile"):
            self.user.applicant_profile.resume = uploaded_resume
            self.user.applicant_profile.save(update_fields=["resume"])

        return self.user

