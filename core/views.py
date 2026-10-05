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
    featured_slugs = [
        "frontend-developer",
        "ui-ux-designer",
        "backend-developer",
        "marketing-manager",
        "product-designer",
        "data-scientist-nlp",
    ]
    jobs_by_slug = {
        j.slug: j
        for j in Job.objects.filter(slug__in=featured_slugs).select_related(
            "employer", "employer__employer_profile", "category"
        ).prefetch_related("tags")
    }
    featured_jobs = [jobs_by_slug[slug] for slug in featured_slugs if slug in jobs_by_slug]
    if len(featured_jobs) < 6:
        extra_jobs = list(
            Job.objects.filter(status=Job.Status.OPEN)
            .exclude(slug__in=[j.slug for j in featured_jobs])
            .select_related("employer", "employer__employer_profile", "category")
            .prefetch_related("tags")[: 6 - len(featured_jobs)]
        )
        featured_jobs.extend(extra_jobs)

    category_slugs = [
        "development",
        "design",
        "marketing",
        "sales",
        "finance",
        "operations",
        "customer-support",
        "hr",
    ]
    cats_by_slug = {c.slug: c for c in Category.objects.filter(slug__in=category_slugs)}
    categories = [cats_by_slug[slug] for slug in category_slugs if slug in cats_by_slug]
    if len(categories) < 8:
        extra_cats = list(Category.objects.exclude(slug__in=[c.slug for c in categories])[: 8 - len(categories)])
        categories.extend(extra_cats)

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
