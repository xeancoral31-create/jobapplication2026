"""moderation/admin.py"""
from django.contrib import admin
from .models import Flag, AuditLog


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = (
        "reason",
        "status",
        "reporter",
        "content_type",
        "object_id",
        "resolved_by",
        "created_at",
    )
    list_filter = ("reason", "status", "content_type", "created_at")
    search_fields = ("reporter__username", "description", "resolution_notes")
    raw_id_fields = ("reporter", "resolved_by")
    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Report",
            {
                "fields": (
                    "reporter",
                    "content_type",
                    "object_id",
                    "reason",
                    "description",
                    "status",
                )
            },
        ),
        (
            "Resolution",
            {"fields": ("resolved_by", "resolution_notes", "resolved_at", "created_at")},
        ),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "actor",
        "action",
        "content_type",
        "object_repr",
        "ip_address",
    )
    list_filter = ("action", "content_type", "timestamp")
    search_fields = ("actor__username", "object_repr", "ip_address")
    readonly_fields = ("timestamp", "actor", "action", "content_type", "object_id", "object_repr", "changes", "ip_address")
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
