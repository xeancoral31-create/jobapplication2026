"""applications/models.py - Application, Interview, and Offer models."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.validators import validate_resume_file


class Application(models.Model):
    """A job seeker's application for a specific job posting."""

    class Status(models.TextChoices):
        SUBMITTED = "submitted", _("Submitted")
        UNDER_REVIEW = "under_review", _("Under Review")
        SHORTLISTED = "shortlisted", _("Shortlisted")
        INTERVIEW_SCHEDULED = "interview_scheduled", _("Interview Scheduled")
        OFFER_EXTENDED = "offer_extended", _("Offer Extended")
        HIRED = "hired", _("Hired")
        REJECTED = "rejected", _("Rejected")
        WITHDRAWN = "withdrawn", _("Withdrawn")

    # Relations
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
        limit_choices_to={"role": "applicant"},
    )
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="applications",
    )

    # Core content
    cover_letter = models.TextField(blank=True)
    resume_snapshot = models.FileField(
        upload_to="application_resumes/",
        blank=True,
        null=True,
        validators=[validate_resume_file],
        help_text="Copy of resume at time of application",
    )
    portfolio_url = models.URLField(blank=True)

    # Tracking
    status = models.CharField(
        max_length=30,
        choices=Status,
        default=Status.SUBMITTED,
        db_index=True,
    )
    employer_notes = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Employer rating 1-5",
    )

    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    withdrawn_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-applied_at"]
        verbose_name = "application"
        verbose_name_plural = "applications"
        # One applicant can apply to the same job only once
        unique_together = [("applicant", "job")]
        constraints = [
            models.UniqueConstraint(
                fields=["applicant", "job"],
                name="unique_application_per_job",
            )
        ]
        indexes = [
            models.Index(fields=["status"], name="app_status_idx"),
            models.Index(fields=["status", "job"], name="app_status_job_idx"),
            models.Index(fields=["status", "applicant"], name="app_status_app_idx"),
            models.Index(fields=["job", "status"], name="app_job_status_idx"),
            models.Index(fields=["applicant", "status"], name="app_applicant_status_idx"),
            models.Index(fields=["job", "-applied_at"], name="app_job_applied_idx"),
        ]

    def __str__(self):
        return f"{self.applicant} → {self.job} [{self.status}]"


class Interview(models.Model):
    """Interview slot linked to an Application."""

    class Format(models.TextChoices):
        PHONE = "phone", _("Phone Screen")
        VIDEO = "video", _("Video Call")
        ONSITE = "onsite", _("On-site")
        TECHNICAL = "technical", _("Technical Assessment")
        PANEL = "panel", _("Panel Interview")

    class Outcome(models.TextChoices):
        PENDING = "pending", _("Pending")
        PASSED = "passed", _("Passed")
        FAILED = "failed", _("Failed")
        NO_SHOW = "no_show", _("No-show")
        RESCHEDULED = "rescheduled", _("Rescheduled")

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews",
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    format = models.CharField(max_length=20, choices=Format, default=Format.VIDEO)
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    interviewer_notes = models.TextField(blank=True)
    outcome = models.CharField(max_length=20, choices=Outcome, default=Outcome.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_at"]
        verbose_name = "interview"
        verbose_name_plural = "interviews"

    def __str__(self):
        return (
            f"Interview ({self.format}) for {self.application} "
            f"@ {self.scheduled_at:%Y-%m-%d %H:%M}"
        )

    @property
    def notes(self):
        return self.interviewer_notes

    @notes.setter
    def notes(self, value):
        self.interviewer_notes = value


class Offer(models.Model):
    """Formal job offer extended to an applicant."""

    class OfferStatus(models.TextChoices):
        PENDING = "pending", _("Pending Response")
        ACCEPTED = "accepted", _("Accepted")
        DECLINED = "declined", _("Declined")
        EXPIRED = "expired", _("Expired")
        NEGOTIATING = "negotiating", _("Negotiating")

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="offer",
    )
    salary_offered = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default="USD")
    start_date = models.DateField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    offer_letter = models.FileField(upload_to="offer_letters/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=OfferStatus, default=OfferStatus.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "offer"
        verbose_name_plural = "offers"

    def __str__(self):
        return f"Offer for {self.application} [{self.status}]"
