"""accounts/admin.py"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, EmployerProfile, ApplicantProfile


class EmployerProfileInline(admin.StackedInline):
    model = EmployerProfile
    extra = 0
    can_delete = False


class ApplicantProfileInline(admin.StackedInline):
    model = ApplicantProfile
    extra = 0
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "get_full_name",
        "role",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    inlines = [EmployerProfileInline, ApplicantProfileInline]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            _("Inkboard Profile"),
            {
                "fields": (
                    "role",
                    "avatar",
                    "bio",
                    "phone",
                    "location",
                    "website",
                )
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            _("Inkboard Profile"),
            {
                "fields": ("role", "email", "first_name", "last_name"),
            },
        ),
    )


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "user",
        "company_size",
        "industry",
        "founded_year",
    )
    list_filter = ("company_size", "industry")
    search_fields = ("company_name", "user__username", "user__email")
    raw_id_fields = ("user",)


@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "headline",
        "experience_level",
        "available_from",
    )
    list_filter = ("experience_level",)
    search_fields = ("user__username", "user__email", "headline", "skills")
    raw_id_fields = ("user",)
