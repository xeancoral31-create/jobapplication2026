"""applications/urls.py"""
from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path("apply/<int:job_id>/", views.apply, name="apply"),
    path("", views.my_applications, name="list"),
    path("<int:pk>/", views.application_detail, name="detail"),
    path("<int:pk>/withdraw/", views.withdraw, name="withdraw"),

    # ── Pipeline Review Endpoints (Stage 5) ───────────────────────────────
    path("<int:pk>/transition/", views.application_transition, name="transition"),
    path("<int:pk>/drawer/", views.application_drawer, name="drawer"),
    path("<int:pk>/schedule-interview/", views.schedule_interview_view, name="schedule_interview"),
    path("interviews/<int:pk>/record-result/", views.record_interview_result_view, name="record_interview_result"),
    path("<int:pk>/resume/", views.download_resume, name="download_resume"),
]
