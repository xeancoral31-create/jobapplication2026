"""jobs/admin.py"""
from django.contrib import admin
from .models import Category, Job, JobTag


class JobTagInline(admin.TabularInline):
    model = JobTag
    extra = 2
    max_num = 20


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "color")
    list_filter = ()
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "employer",
        "category",
        "status",
        "job_type",
        "experience_level",
        "location",
        "is_remote",
        "deadline",
        "created_at",
    )
    list_filter = (
        "status",
        "job_type",
        "experience_level",
        "is_remote",
        "category",
        "created_at",
    )
    search_fields = ("title", "description", "location", "employer__username")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("employer", "category")
    date_hierarchy = "created_at"
    inlines = [JobTagInline]
    readonly_fields = ("views_count", "created_at", "updated_at")

    fieldsets = (
        (
            "Basics",
            {
                "fields": (
                    "employer",
                    "category",
                    "title",
                    "slug",
                    "status",
                    "job_type",
                    "experience_level",
                )
            },
        ),
        (
            "Location",
            {"fields": ("location", "is_remote")},
        ),
        (
            "Description",
            {"fields": ("description", "requirements", "responsibilities", "benefits")},
        ),
        (
            "Salary",
            {"fields": ("salary_min", "salary_max", "salary_period", "salary_currency")},
        ),
        (
            "Dates & Stats",
            {"fields": ("deadline", "views_count", "created_at", "updated_at")},
        ),
    )


@admin.register(JobTag)
class JobTagAdmin(admin.ModelAdmin):
    list_display = ("name", "job")
    list_filter = ()
    search_fields = ("name", "job__title")
    raw_id_fields = ("job",)
