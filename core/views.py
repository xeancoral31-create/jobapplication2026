"""core/views.py — Home, role dashboards, error handlers."""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from jobs.models import Job, Category


# ── Error handlers ─────────────────────────────────────────────────────────

def custom_403(request, exception=None):
    ctx = {}
    if hasattr(exception, "args") and exception.args:
        ctx["message"] = str(exception.args[0])
    return render(request, "403.html", ctx, status=403)


def custom_404(request, exception=None):
    return render(request, "404.html", {}, status=404)


# ── Public ─────────────────────────────────────────────────────────────────

def home(request):
    featured_jobs = list(
        Job.objects.filter(status=Job.Status.OPEN)
        .select_related("employer", "employer__employer_profile", "category")
        .prefetch_related("tags")
        .order_by("-created_at")[:6]
    )

    categories = list(Category.objects.all().order_by("name"))

    career_fields = [
        {"slug": "information-technology", "name": "Information Technology", "icon": "💻", "desc": "Software, Cloud, Cybersecurity & Systems", "color": "#3b82f6"},
        {"slug": "nursing-and-healthcare", "name": "Nursing & Healthcare", "icon": "🩺", "desc": "Clinical Nursing, ICU, Diagnostics & Healthcare", "color": "#06b6d4"},
        {"slug": "education", "name": "Education", "icon": "📚", "desc": "Teaching, Higher Education, Academic & Special Ed", "color": "#8b5cf6"},
        {"slug": "engineering", "name": "Engineering", "icon": "⚙️", "desc": "Civil, Mechanical, Electrical & Structural", "color": "#f59e0b"},
        {"slug": "business-and-finance", "name": "Business & Finance", "icon": "💼", "desc": "Finance, Accounting, Operations, HR & Strategy", "color": "#10b981"},
        {"slug": "hospitality-and-tourism", "name": "Hospitality & Tourism", "icon": "🏨", "desc": "Hotel Operations, Culinary Arts & Tourism", "color": "#ec4899"},
        {"slug": "government-and-public-service", "name": "Government & Public Service", "icon": "🏛️", "desc": "Public Administration, Civic Policy & Social Work", "color": "#6366f1"},
        {"slug": "uniformed-personnel", "name": "Uniformed Personnel", "icon": "🎖️", "desc": "Army, Navy, Coast Guard & Police Services", "color": "#14b8a6"},
        {"slug": "other-professional-fields", "name": "Other Professional Fields", "icon": "🌐", "desc": "Legal, Architecture, Design & Specialized Fields", "color": "#64748b"},
    ]

    uniformed_branches = [
        {"slug": "army", "name": "Army", "icon": "🪖", "desc": "Tactical defense, combat medicine & military logistics"},
        {"slug": "navy", "name": "Navy", "icon": "⚓", "desc": "Fleet operations, marine engineering & navigation"},
        {"slug": "coast_guard", "name": "Coast Guard", "icon": "🚢", "desc": "Maritime safety, search and rescue & coastal protection"},
        {"slug": "police", "name": "Police", "icon": "👮", "desc": "Public safety, community policing & criminal investigation"},
    ]

    total_jobs = Job.objects.filter(status=Job.Status.OPEN).count()

    return render(
        request,
        "core/home.html",
        {
            "featured_jobs": featured_jobs,
            "categories": categories,
            "career_fields": career_fields,
            "uniformed_branches": uniformed_branches,
            "total_jobs": total_jobs,
        },
    )


def styleguide(request):
    """Living style guide — shows all design tokens and components."""
    return render(request, "core/styleguide.html", {})


# ── Generic dashboard (legacy redirect) ────────────────────────────────────

@login_required
def dashboard(request):
    from accounts.views import _role_redirect_url
    return redirect(_role_redirect_url(request.user))


# ── Applicant area ─────────────────────────────────────────────────────────

@login_required
def applicant_dashboard(request):
    from accounts.models import User
    from .services import get_applicant_dashboard_data

    if request.user.role != User.Role.APPLICANT:
        raise PermissionDenied("Applicant access only.")

    ctx = get_applicant_dashboard_data(request.user)
    return render(request, "applicant/dashboard.html", ctx)


# ── Employer area ──────────────────────────────────────────────────────────

@login_required
def employer_dashboard(request):
    from accounts.models import User
    from .services import get_employer_dashboard_data

    if request.user.role != User.Role.EMPLOYER:
        raise PermissionDenied("Employer access only.")

    ctx = get_employer_dashboard_data(request.user)
    return render(request, "employer/dashboard.html", ctx)


def employer_pending(request):
    """Landing page for newly-registered employers awaiting approval."""
    return render(request, "employer/pending.html", {})


# ── Admin panel ────────────────────────────────────────────────────────────

@login_required
def admin_panel(request):
    from .admin_panel_views import admin_panel_dashboard
    return admin_panel_dashboard(request)
