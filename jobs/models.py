from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    """Job category / department bucket."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=60,
        blank=True,
        help_text="CSS icon class or emoji, e.g. '💻' or 'bi-code'",
    )
    color = models.CharField(
        max_length=7,
        default="#6C63FF",
        help_text="Hex color used in the UI, e.g. #6C63FF",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Job(models.Model):
    """A job listing posted by an employer."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        OPEN = "open", _("Open")
        PAUSED = "paused", _("Paused")
        CLOSED = "closed", _("Closed")
        FILLED = "filled", _("Filled")
        REMOVED = "removed", _("Removed")

    class JobType(models.TextChoices):
        FULL_TIME = "full_time", _("Full-time")
        PART_TIME = "part_time", _("Part-time")
        CONTRACT = "contract", _("Contract")
        FREELANCE = "freelance", _("Freelance")
        INTERNSHIP = "internship", _("Internship")
        TEMPORARY = "temporary", _("Temporary")

    class ExperienceLevel(models.TextChoices):
        ENTRY = "entry", _("Entry Level")
        MID = "mid", _("Mid Level")
        SENIOR = "senior", _("Senior Level")
        EXECUTIVE = "executive", _("Executive")

    class SalaryPeriod(models.TextChoices):
        HOURLY = "hourly", _("Per Hour")
        MONTHLY = "monthly", _("Per Month")
        YEARLY = "yearly", _("Per Year")

    # Relations
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posted_jobs",
        limit_choices_to={"role": "employer"},
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )

    # Core fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    benefits = models.TextField(blank=True)

    # Classification
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
        db_index=True,
    )
    job_type = models.CharField(max_length=20, choices=JobType, default=JobType.FULL_TIME)
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel,
        default=ExperienceLevel.MID,
    )

    # Location
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)

    # Salary
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_period = models.CharField(
        max_length=20,
        choices=SalaryPeriod,
        default=SalaryPeriod.YEARLY,
        blank=True,
    )
    salary_currency = models.CharField(max_length=5, default="USD")

    # Dates
    deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Stats (denormalised for fast listing)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "job"
        verbose_name_plural = "jobs"
        indexes = [
            models.Index(fields=["status"], name="job_status_idx"),
            models.Index(fields=["status", "-created_at"], name="job_status_created_idx"),
            models.Index(fields=["status", "employer"], name="job_status_emp_idx"),
            models.Index(fields=["status", "category"], name="job_status_cat_idx"),
            models.Index(fields=["employer", "status"], name="job_emp_status_idx"),
        ]

    def __str__(self):
        return f"{self.title} @ {self.employer}"

    def is_open(self):
        return self.status == self.Status.OPEN

    def is_draft(self):
        return self.status == self.Status.DRAFT

    def is_closed(self):
        return self.status == self.Status.CLOSED

    def is_removed(self):
        return self.status == self.Status.REMOVED

    def clean(self):
        super().clean()
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_min > self.salary_max:
                raise ValidationError({
                    "salary_min": _("Minimum salary cannot be greater than maximum salary."),
                    "salary_max": _("Maximum salary cannot be less than minimum salary."),
                })

        if self.deadline:
            today = timezone.now().date()
            if self.deadline < today:
                raise ValidationError({
                    "deadline": _("Deadline cannot be in the past."),
                })

        if self.employer_id and self.status == self.Status.OPEN:
            employer = self.employer
            if hasattr(employer, "is_verified") and not employer.is_verified:
                raise ValidationError({
                    "status": _("Unverified employers can only save drafts. Your account is pending verification."),
                })

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "job"
            unique_slug = base_slug
            num = 1
            while Job.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def close(self):
        self.status = self.Status.CLOSED
        self.save(update_fields=["status", "updated_at"])

    def reopen(self):
        if hasattr(self.employer, "is_verified") and not self.employer.is_verified:
            raise ValidationError(_("Unverified employers cannot publish or reopen jobs."))
        self.status = self.Status.OPEN
        self.save(update_fields=["status", "updated_at"])

    def soft_delete(self):
        self.status = self.Status.REMOVED
        self.save(update_fields=["status", "updated_at"])

    def salary_display(self):
        if self.salary_min and self.salary_max:
            return (
                f"{self.salary_currency} {self.salary_min:,.0f}–"
                f"{self.salary_max:,.0f} / {self.salary_period}"
            )
        return "Salary not specified"


class JobTag(models.Model):
    """Free-text skill / technology tag attached to a job."""

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=60)

    class Meta:
        ordering = ["name"]
        unique_together = [("job", "name")]
        verbose_name = "job tag"
        verbose_name_plural = "job tags"

    def __str__(self):
        return self.name
