"""applications/admin.py"""
from django.contrib import admin
from .models import Application, Interview, Offer


class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0
    readonly_fields = ("created_at",)


class OfferInline(admin.StackedInline):
    model = Offer
    extra = 0
    can_delete = False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "applicant",
        "job",
        "status",
        "rating",
        "applied_at",
        "updated_at",
    )
    list_filter = ("status", "applied_at", "job__category")
    search_fields = (
        "applicant__username",
        "applicant__email",
        "job__title",
        "employer_notes",
    )
    raw_id_fields = ("applicant", "job")
    readonly_fields = ("applied_at", "updated_at")
    inlines = [InterviewInline, OfferInline]

    fieldsets = (
        (
            "Application",
            {"fields": ("applicant", "job", "status", "rating")},
        ),
        (
            "Content",
            {"fields": ("cover_letter", "resume_snapshot", "portfolio_url")},
        ),
        (
            "Employer Notes",
            {"fields": ("employer_notes", "withdrawn_at")},
        ),
        (
            "Timestamps",
            {"fields": ("applied_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "format",
        "scheduled_at",
        "duration_minutes",
        "outcome",
    )
    list_filter = ("format", "outcome", "scheduled_at")
    search_fields = (
        "application__applicant__username",
        "application__job__title",
    )
    raw_id_fields = ("application",)
    readonly_fields = ("created_at",)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "salary_offered",
        "currency",
        "status",
        "start_date",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = (
        "application__applicant__username",
        "application__job__title",
    )
    raw_id_fields = ("application",)
    readonly_fields = ("created_at", "updated_at")
