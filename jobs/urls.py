"""jobs/urls.py"""
from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    # ── Public Job Browsing ────────────────────────────────────────────────
    path("", views.job_list, name="list"),
    path("category/<slug:slug>/", views.category_detail, name="category"),

    # ── Employer Management (Specific routes before <slug:slug>/) ──────────
    path("manage/", views.employer_job_list, name="manage_list"),
    path("post/", views.job_create, name="create"),
    path("preview/", views.job_preview_card, name="preview_card"),

    # ── Job Specific Actions (by slug) ─────────────────────────────────────
    path("<slug:slug>/edit/", views.job_edit, name="edit"),
    path("<slug:slug>/close/", views.job_close, name="close"),
    path("<slug:slug>/reopen/", views.job_reopen, name="reopen"),
    path("<slug:slug>/delete/", views.job_delete, name="delete"),
    path("<slug:slug>/pipeline/", views.job_pipeline, name="pipeline"),

    # ── Public Job Detail (Last) ───────────────────────────────────────────
    path("<slug:slug>/", views.job_detail, name="detail"),
]
