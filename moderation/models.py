"""moderation/models.py - Content flag and audit log."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class Flag(models.Model):
    """User-submitted content report / flag."""

    class Reason(models.TextChoices):
        SPAM = "spam", _("Spam")
        INAPPROPRIATE = "inappropriate", _("Inappropriate Content")
        MISLEADING = "misleading", _("Misleading Information")
        DUPLICATE = "duplicate", _("Duplicate Listing")
        SCAM = "scam", _("Potential Scam")
        OTHER = "other", _("Other")

    class FlagStatus(models.TextChoices):
        OPEN = "open", _("Open")
        UNDER_REVIEW = "under_review", _("Under Review")
        RESOLVED = "resolved", _("Resolved")
        DISMISSED = "dismissed", _("Dismissed")

    # Who flagged
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="flags_raised",
    )
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    reason = models.CharField(max_length=30, choices=Reason, default=Reason.SPAM)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=FlagStatus, default=FlagStatus.OPEN)

    # Resolution
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flags_resolved",
    )
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "flag"
        verbose_name_plural = "flags"

    def __str__(self):
        return f"Flag [{self.reason}] on {self.content_type} #{self.object_id}"


class AuditLog(models.Model):
    """Immutable audit trail of admin / moderation actions."""

    class Action(models.TextChoices):
        CREATE = "create", _("Created")
        UPDATE = "update", _("Updated")
        DELETE = "delete", _("Deleted")
        APPROVE = "approve", _("Approved")
        REJECT = "reject", _("Rejected")
        BAN = "ban", _("Banned")
        RESTORE = "restore", _("Restored")
        SUSPEND = "suspend", _("Suspended")
        REACTIVATE = "reactivate", _("Reactivated")
        REMOVE = "remove", _("Removed")

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_actions",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.PositiveBigIntegerField(blank=True, null=True)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.PositiveBigIntegerField(blank=True, null=True)
    object_repr = models.CharField(max_length=400)
    action = models.CharField(max_length=30, choices=Action.choices)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "audit log"
        verbose_name_plural = "audit logs"

    def __str__(self):
        user_display = self.admin or self.actor
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {user_display} — {self.action} {self.object_repr}"

    def save(self, *args, **kwargs):
        # Sync actor and admin
        if self.admin and not self.actor:
            self.actor = self.admin
        elif self.actor and not self.admin:
            self.admin = self.actor

        # Sync object_id and target_id
        if self.target_id is not None and self.object_id is None:
            self.object_id = self.target_id
        elif self.object_id is not None and self.target_id is None:
            self.target_id = self.object_id

        # Sync content_type and target_type
        if not self.target_type and self.content_type:
            self.target_type = self.content_type.model
        elif self.target_type and not self.content_type:
            try:
                from django.apps import apps
                for model in apps.get_models():
                    if model._meta.model_name.lower() == self.target_type.lower():
                        self.content_type = ContentType.objects.get_for_model(model)
                        break
            except Exception:
                pass

        if not self.object_repr:
            self.object_repr = f"{self.target_type or 'object'} #{self.target_id or self.object_id}"

        super().save(*args, **kwargs)


# Alias for admin audit trail
AdminAction = AuditLog

def log_admin_action(*args, **kwargs):
    from moderation.services import log_admin_action as _log
    return _log(*args, **kwargs)

AdminAction.log = staticmethod(log_admin_action)

