"""core/models.py — Persistent per-user notifications."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """A single notification delivered to one user. Read state is stored server-side."""

    class Kind(models.TextChoices):
        JOB = "job", "Job Opportunity"
        LISTING = "listing", "New Listing"
        PLATFORM = "platform", "Platform Update"
        APPLICATION = "application", "Application Update"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.PLATFORM)
    # Rendered as "<message> <strong>highlight</strong>" in the dropdown.
    message = models.CharField(max_length=255)
    highlight = models.CharField(max_length=120, blank=True)
    detail_title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status_label = models.CharField(max_length=60, blank=True)
    pills = models.JSONField(default=list, blank=True)
    action_url = models.CharField(max_length=255, blank=True)
    action_text = models.CharField(max_length=60, blank=True)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "is_read"])]

    def __str__(self):
        return f"{self.user} · {self.message[:40]} ({'read' if self.is_read else 'unread'})"

    @property
    def title(self):
        return self.detail_title or f"{self.message} {self.highlight}".strip()

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
