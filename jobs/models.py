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

    def get_svg_icon(self, size=14, stroke_width=2, extra_class=""):
        """Return a clean, professional inline SVG icon string."""
        from django.utils.safestring import mark_safe

        slug_val = (self.slug or "").lower()
        icon_val = (self.icon or "").lower()
        key = icon_val or slug_val

        # SVGs mapped to categories / icon identifiers
        if any(k in key for k in ["army", "shield-star"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>'
                f'<polygon points="12 8 13.5 11.5 17 11.8 14.3 14.2 15.1 17.7 12 15.8 8.9 17.7 9.7 14.2 7 11.8 10.5 11.5 12 8"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["business", "briefcase", "finance"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<rect width="20" height="14" x="2" y="7" rx="2"/>'
                f'<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["coast-guard", "coast_guard", "life-buoy", "buoy"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<circle cx="12" cy="12" r="10"/>'
                f'<path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/>'
                f'<circle cx="12" cy="12" r="4"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["data", "chart", "analytics"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/><circle cx="14" cy="14" r="1.5"/><circle cx="19" cy="9" r="1.5"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["design", "palette", "creative"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/>'
                f'<circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>'
                f'<path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.563-2.512 5.563-5.563C21.938 6.5 17.5 2 12 2Z"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["education", "graduation-cap", "academic", "school"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/>'
                f'<path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["engineering", "settings", "gear", "cog"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
                f'<circle cx="12" cy="12" r="3"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["health", "heart-pulse", "nursing", "medical"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>'
                f'<path d="M12 5v6"/><path d="M9 8h6"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["hospitality", "hotel", "building", "tourism"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/>'
                f'<path d="M6 12H4a2 2 0 0 0-2 2v8"/><path d="M18 9h2a2 2 0 0 1 2 2v11"/>'
                f'<path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["it", "tech", "laptop", "code", "dev"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<rect width="20" height="14" x="2" y="3" rx="2"/>'
                f'<line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["marketing", "megaphone"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["navy", "anchor"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<circle cx="12" cy="5" r="3"/><line x1="12" x2="12" y1="22" y2="8"/><path d="M5 12H2a10 10 0 0 0 20 0h-3"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["police", "shield-check"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["product", "folder"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<path d="M20 7h-3a2 2 0 0 1-2-2V2"/><path d="M9 18a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h7l4 4v10a2 2 0 0 1-2 2Z"/>'
                f'<path d="M3 7.6v12.8A1.6 1.6 0 0 0 4.6 22h11"/>'
                f'</svg>'
            )
        elif any(k in key for k in ["government", "landmark"]):
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<line x1="2" x2="22" y1="22" y2="22"/><line x1="12" x2="12" y1="2" y2="6"/><path d="m2 6 10-4 10 4Z"/>'
                f'<line x1="6" x2="6" y1="10" y2="18"/><line x1="10" x2="10" y1="10" y2="18"/><line x1="14" x2="14" y1="10" y2="18"/><line x1="18" x2="18" y1="10" y2="18"/>'
                f'</svg>'
            )
        else:
            svg = (
                f'<svg class="{extra_class}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                f'stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                f'<rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
                f'</svg>'
            )
        return mark_safe(svg)

    @property
    def svg_icon(self):
        """Property returning standard 14px SVG icon for badges, tags, and cards."""
        return self.get_svg_icon(size=14)


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
        FULL_TIME = "full_time", _("Full-Time")
        PART_TIME = "part_time", _("Part-Time")
        CONTRACT = "contract", _("Contractual")
        CONTRACTUAL = "contractual", _("Contractual")
        FREELANCE = "freelance", _("Freelance")
        INTERNSHIP = "internship", _("Internship")
        TEMPORARY = "temporary", _("Temporary")

    class JobField(models.TextChoices):
        IT = "it", _("Information Technology")
        HEALTHCARE = "healthcare", _("Nursing & Healthcare")
        EDUCATION = "education", _("Education")
        ENGINEERING = "engineering", _("Engineering")
        BUSINESS = "business", _("Business & Finance")
        HOSPITALITY = "hospitality", _("Hospitality & Tourism")
        GOVERNMENT = "government", _("Government & Public Service")
        UNIFORMED = "uniformed", _("Uniformed Personnel")
        OTHER = "other", _("Other Professional Fields")

    class UniformedBranch(models.TextChoices):
        ARMY = "army", _("Army")
        NAVY = "navy", _("Navy")
        COAST_GUARD = "coast_guard", _("Coast Guard")
        POLICE = "police", _("Police")

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
    job_field = models.CharField(
        max_length=100,
        choices=JobField.choices,
        blank=True,
        default="",
        db_index=True,
        help_text="Broad career field, e.g. Healthcare, Education, Engineering, Uniformed Personnel",
    )
    uniformed_branch = models.CharField(
        max_length=20,
        choices=UniformedBranch.choices,
        blank=True,
        default="",
        db_index=True,
        help_text="Branch for Uniformed Personnel listings (Army / Navy / Coast Guard / Police)",
    )
    department = models.CharField(
        max_length=120,
        blank=True,
        default="",
        db_index=True,
        help_text="Department or service unit, e.g. Nursing Services, Fleet Operations, Emergency Medicine",
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
