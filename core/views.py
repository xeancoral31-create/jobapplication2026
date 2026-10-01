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
    featured_jobs = Job.objects.filter(status=Job.Status.OPEN).select_related(
        "employer", "category"
    )[:6]
    categories = Category.objects.all()[:8]
    return render(
        request,
        "core/home.html",
        {"featured_jobs": featured_jobs, "categories": categories},
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
