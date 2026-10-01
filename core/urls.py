"""core/urls.py"""
from django.urls import path
from . import views
from . import admin_panel_views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("styleguide/", views.styleguide, name="styleguide"),
    # Role dashboards
    path("applicant/",         views.applicant_dashboard, name="applicant_dashboard"),
    path("employer/",          views.employer_dashboard,  name="employer_dashboard"),
    path("employer/pending/",  views.employer_pending,    name="employer_pending"),
    path("admin-panel/",                       views.admin_panel,                                 name="admin_panel"),
    path("admin-panel/users/",                 admin_panel_views.admin_user_list,                 name="admin_users"),
    path("admin-panel/users/<int:pk>/suspend/", admin_panel_views.admin_user_suspend,             name="admin_user_suspend"),
    path("admin-panel/users/<int:pk>/reactivate/", admin_panel_views.admin_user_reactivate,       name="admin_user_reactivate"),
    path("admin-panel/verifications/",         admin_panel_views.admin_verification_queue,        name="admin_verifications"),
    path("admin-panel/verifications/<int:pk>/approve/", admin_panel_views.admin_employer_approve, name="admin_employer_approve"),
    path("admin-panel/verifications/<int:pk>/reject/",  admin_panel_views.admin_employer_reject,  name="admin_employer_reject"),
    path("admin-panel/employers/<int:pk>/approve/", admin_panel_views.admin_employer_approve,     name="admin_employer_approve_alt"),
    path("admin-panel/employers/<int:pk>/reject/",  admin_panel_views.admin_employer_reject,      name="admin_employer_reject_alt"),
    path("admin-panel/jobs/",                  admin_panel_views.admin_job_list,                  name="admin_jobs"),
    path("admin-panel/jobs/<int:pk>/remove/",  admin_panel_views.admin_job_remove,                name="admin_job_remove"),
    path("admin-panel/jobs/<int:pk>/moderate/", admin_panel_views.admin_job_remove,               name="admin_job_moderate"),
    path("admin-panel/audit-log/",             admin_panel_views.admin_audit_log,                 name="admin_audit_log"),
    path("admin-panel/audit/",                 admin_panel_views.admin_audit_log,                 name="admin_audit_log_alt"),
]
