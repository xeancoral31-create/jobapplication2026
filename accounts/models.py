"""accounts/models.py - Custom User with role-based profile split."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.validators import validate_resume_file


class User(AbstractUser):
    """Extends AbstractUser with a role field and shared profile fields."""

    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        EMPLOYER = "employer", _("Employer")
        APPLICANT = "applicant", _("Applicant")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        PENDING = "pending", _("Pending Approval")
        SUSPENDED = "suspended", _("Suspended")

    class AccessLevel(models.TextChoices):
        MODERATOR = "moderator", _("Moderator")
        SUPERADMIN = "superadmin", _("Superadmin")

    role = models.CharField(
        max_length=20,
        choices=Role,
        default=Role.APPLICANT,
    )
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.MODERATOR,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.ACTIVE,
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER

    @property
    def is_applicant(self):
        return self.role == self.Role.APPLICANT

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def is_superadmin(self):
        if self.access_level == self.AccessLevel.SUPERADMIN:
            return True
        if self.is_superuser and self.access_level != self.AccessLevel.MODERATOR:
            return True
        return False

    @property
    def is_moderator(self):
        return (
            (self.role == self.Role.ADMIN or self.is_staff)
            and not self.is_superadmin
        )

    def can_suspend_users(self):
        return self.is_superadmin

    def save(self, *args, **kwargs):
        if self.is_superuser and not self.access_level:
            self.access_level = self.AccessLevel.SUPERADMIN
        super().save(*args, **kwargs)

    @property
    def is_suspended(self):
        return self.status == self.Status.SUSPENDED

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_verified(self):
        if hasattr(self, "_is_verified_override"):
            return self._is_verified_override
        return self.status == self.Status.ACTIVE

    @is_verified.setter
    def is_verified(self, val):
        self._is_verified_override = bool(val)
        if val:
            self.status = self.Status.ACTIVE
        else:
            self.status = self.Status.PENDING


class EmployerProfile(models.Model):
    """Extended profile data for employers / companies."""

    class CompanySize(models.TextChoices):
        SOLO = "1-10", _("1–10 employees")
        SMALL = "11-50", _("11–50 employees")
        MEDIUM = "51-200", _("51–200 employees")
        LARGE = "201-1000", _("201–1 000 employees")
        ENTERPRISE = "1000+", _("1 000+ employees")

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="employer_profile",
    )
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    company_description = models.TextField(blank=True)
    company_size = models.CharField(
        max_length=20,
        choices=CompanySize,
        default=CompanySize.SMALL,
    )
    industry = models.CharField(max_length=120, blank=True)
    founded_year = models.PositiveSmallIntegerField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True)

    class Meta:
        ordering = ["company_name"]
        verbose_name = "employer profile"
        verbose_name_plural = "employer profiles"

    def __str__(self):
        return self.company_name

    @property
    def is_verified(self):
        return self.user.is_verified

    @is_verified.setter
    def is_verified(self, val):
        self.user.is_verified = val


class ApplicantProfile(models.Model):
    """Extended profile data for job seekers."""

    class ExperienceLevel(models.TextChoices):
        ENTRY = "entry", _("Entry Level")
        MID = "mid", _("Mid Level")
        SENIOR = "senior", _("Senior Level")
        EXECUTIVE = "executive", _("Executive")

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="applicant_profile",
    )
    headline = models.CharField(max_length=200, blank=True)
    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True,
        validators=[validate_resume_file],
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel,
        default=ExperienceLevel.ENTRY,
    )
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated list of skills",
    )
    available_from = models.DateField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]
        verbose_name = "applicant profile"
        verbose_name_plural = "applicant profiles"

    def __str__(self):
        return f"{self.user} — {self.headline or 'No headline'}"

    def skills_list(self):
        """Return skills as a clean Python list."""
        return [s.strip() for s in self.skills.split(",") if s.strip()]
