"""jobs/views.py — Public job listings and Employer Job CRUD."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from .forms import JobForm
from .models import Category, Job


# ── Public Job Views ──────────────────────────────────────────────────────────

def job_list(request):
    """Public browse jobs list with search, category, location, salary filters and HTMX pagination."""
    today = timezone.now().date()
    qs = (
        Job.objects.filter(status=Job.Status.OPEN)
        .filter(Q(deadline__gte=today) | Q(deadline__isnull=True))
        .select_related("employer", "employer__employer_profile", "category")
        .order_by("-created_at")
    )

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(employer__employer_profile__company_name__icontains=q)
            | Q(location__icontains=q)
        )

    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    location = request.GET.get("location", "").strip()
    if location:
        qs = qs.filter(location__icontains=location)

    is_remote = request.GET.get("is_remote")
    if is_remote in ["1", "true", "True", "on"]:
        qs = qs.filter(is_remote=True)

    min_salary = request.GET.get("min_salary", "").strip()
    if min_salary:
        try:
            val = float(min_salary)
            qs = qs.filter(Q(salary_max__gte=val) | (Q(salary_min__gte=val) & Q(salary_max__isnull=True)))
        except ValueError:
            pass

    paginator = Paginator(qs, 6)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all().order_by("name")

    context = {
        "page_obj": page_obj,
        "jobs": page_obj.object_list,
        "categories": categories,
        "total_count": paginator.count,
        "selected_category": category_slug,
        "search_query": q,
        "selected_location": location,
        "is_remote": bool(is_remote in ["1", "true", "True", "on"]),
        "min_salary": min_salary,
    }

    if request.headers.get("HX-Request"):
        return render(request, "jobs/partials/job_list_results.html", context)

    return render(request, "jobs/list.html", context)


def job_detail(request, slug):
    """Public job detail page with application state and apply button."""
    job = get_object_or_404(
        Job.objects.select_related("employer", "employer__employer_profile", "category"),
        slug=slug,
    )
    # Only allow viewing non-open jobs if employer owns it or user is staff
    if not job.is_open():
        if not (request.user.is_authenticated and (job.employer == request.user or request.user.is_staff)):
            raise PermissionDenied("This job listing is no longer active.")

    existing_application = None
    if request.user.is_authenticated and request.user.role == User.Role.APPLICANT:
        existing_application = job.applications.filter(applicant=request.user).first()

    today = timezone.now().date()
    is_active = job.is_open() and (job.deadline is None or job.deadline >= today)

    return render(request, "jobs/detail.html", {
        "job": job,
        "has_applied": bool(existing_application),
        "existing_application": existing_application,
        "is_active": is_active,
    })


def category_detail(request, slug):
    """Category filter view."""
    category = get_object_or_404(Category, slug=slug)
    jobs = (
        category.jobs.filter(status=Job.Status.OPEN)
        .select_related("employer", "employer__employer_profile")
        .order_by("-created_at")
    )
    return render(request, "jobs/category.html", {"category": category, "jobs": jobs})


# ── Employer Job Management (CRUD) ────────────────────────────────────────────

def _ensure_employer(user):
    """Raise PermissionDenied if user is not an employer."""
    if not user.is_authenticated or user.role != User.Role.EMPLOYER:
        raise PermissionDenied("Employer access required.")


@login_required
def employer_job_list(request):
    """List employer jobs with status tabs (Draft/Open/Closed) and application counts."""
    _ensure_employer(request.user)

    # Status tabs filter
    active_tab = request.GET.get("status", "all").lower()

    # Aggregate counts across all non-removed statuses (1 query)
    counts = Job.objects.filter(employer=request.user).exclude(status=Job.Status.REMOVED).aggregate(
        all_count=Count("id"),
        open_count=Count("id", filter=Q(status=Job.Status.OPEN)),
        draft_count=Count("id", filter=Q(status=Job.Status.DRAFT)),
        closed_count=Count("id", filter=Q(status=Job.Status.CLOSED)),
    )

    qs = (
        Job.objects.filter(employer=request.user)
        .exclude(status=Job.Status.REMOVED)
        .select_related("category")
        .annotate(applicant_count=Count("applications"))
        .order_by("-created_at")
    )

    if active_tab == "open":
        qs = qs.filter(status=Job.Status.OPEN)
    elif active_tab == "draft":
        qs = qs.filter(status=Job.Status.DRAFT)
    elif active_tab == "closed":
        qs = qs.filter(status=Job.Status.CLOSED)

    return render(request, "jobs/manage_list.html", {
        "jobs": qs,
        "active_tab": active_tab,
        "counts": counts,
        "is_verified": getattr(request.user, "is_verified", True),
    })


@login_required
def job_create(request):
    """Create a new job posting with category select and live preview."""
    _ensure_employer(request.user)

    is_verified = getattr(request.user, "is_verified", True)

    if request.method == "POST":
        form = JobForm(request.POST, employer=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            # Extra safety check: unverified employers cannot publish
            if not is_verified and job.status == Job.Status.OPEN:
                job.status = Job.Status.DRAFT
                messages.warning(request, "Your account is pending verification. Job saved as a draft.")
            else:
                if job.status == Job.Status.OPEN:
                    messages.success(request, f'Job "{job.title}" has been published successfully!')
                else:
                    messages.success(request, f'Job "{job.title}" saved as draft.')
            job.save()
            return redirect("jobs:manage_list")
    else:
        initial_status = Job.Status.OPEN if is_verified else Job.Status.DRAFT
        form = JobForm(employer=request.user, initial={"status": initial_status})

    return render(request, "jobs/create.html", {
        "form": form,
        "is_verified": is_verified,
        "action": "create",
    })


@login_required
def job_edit(request, slug):
    """Edit an existing job posting. Only the owner can edit."""
    _ensure_employer(request.user)
    job = get_object_or_404(Job, slug=slug)

    # Ownership check
    if job.employer != request.user:
        raise PermissionDenied("You do not have permission to edit this job.")

    is_verified = getattr(request.user, "is_verified", True)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job, employer=request.user)
        if form.is_valid():
            updated_job = form.save(commit=False)
            # Extra safety check: unverified employers cannot publish
            if not is_verified and updated_job.status == Job.Status.OPEN:
                updated_job.status = Job.Status.DRAFT
                messages.warning(request, "Your account is pending verification. Job saved as a draft.")
            else:
                messages.success(request, f'Job "{updated_job.title}" updated successfully.')
            updated_job.save()
            return redirect("jobs:manage_list")
    else:
        form = JobForm(instance=job, employer=request.user)

    return render(request, "jobs/edit.html", {
        "form": form,
        "job": job,
        "is_verified": is_verified,
        "action": "edit",
    })


@login_required
def job_close(request, slug):
    """Close an active job. Only owner can touch a job."""
    _ensure_employer(request.user)
    job = get_object_or_404(Job, slug=slug)

    if job.employer != request.user:
        raise PermissionDenied("You do not have permission to modify this job.")

    if request.method in ["POST", "GET"]:
        job.close()
        messages.success(request, f'Job "{job.title}" has been closed.')

    return redirect("jobs:manage_list")


@login_required
def job_reopen(request, slug):
    """Reopen a closed job. Only owner can touch a job, unverified cannot publish."""
    _ensure_employer(request.user)
    job = get_object_or_404(Job, slug=slug)

    if job.employer != request.user:
        raise PermissionDenied("You do not have permission to modify this job.")

    is_verified = getattr(request.user, "is_verified", True)
    if not is_verified:
        raise PermissionDenied("Unverified employers cannot publish or reopen jobs.")

    if request.method in ["POST", "GET"]:
        try:
            job.reopen()
            messages.success(request, f'Job "{job.title}" has been reopened and published.')
        except ValidationError as e:
            messages.error(request, str(e))

    return redirect("jobs:manage_list")


@login_required
def job_delete(request, slug):
    """Soft delete a job (status=removed). Only owner can touch a job."""
    _ensure_employer(request.user)
    job = get_object_or_404(Job, slug=slug)

    if job.employer != request.user:
        raise PermissionDenied("You do not have permission to delete this job.")

    if request.method in ["POST", "GET"]:
        job.soft_delete()
        messages.success(request, f'Job "{job.title}" has been removed.')

    return redirect("jobs:manage_list")


# ── HTMX Live Preview Card Endpoint ──────────────────────────────────────────

def job_preview_card(request):
    """HTMX partial endpoint: renders live applicant-view preview card."""
    category = None
    category_id = request.POST.get("category") or request.GET.get("category")
    if category_id:
        try:
            category = Category.objects.filter(pk=category_id).first()
        except (ValueError, TypeError):
            category = None

    salary_min = request.POST.get("salary_min") or None
    salary_max = request.POST.get("salary_max") or None

    try:
        salary_min = float(salary_min) if salary_min else None
    except ValueError:
        salary_min = None

    try:
        salary_max = float(salary_max) if salary_max else None
    except ValueError:
        salary_max = None

    mock_job = Job(
        title=request.POST.get("title") or "Job Title",
        category=category,
        job_type=request.POST.get("job_type") or Job.JobType.FULL_TIME,
        experience_level=request.POST.get("experience_level") or Job.ExperienceLevel.MID,
        location=request.POST.get("location") or "Location",
        is_remote=request.POST.get("is_remote") in ["true", "True", "1", "on"],
        salary_min=salary_min,
        salary_max=salary_max,
        salary_period=request.POST.get("salary_period") or Job.SalaryPeriod.YEARLY,
        salary_currency=request.POST.get("salary_currency") or "USD",
        description=request.POST.get("description") or "",
        status=request.POST.get("status") or Job.Status.OPEN,
    )

    employer = request.user if request.user.is_authenticated else None

    return render(request, "jobs/partials/preview_card.html", {
        "job": mock_job,
        "employer": employer,
    })


# ── Candidate Pipeline (Stage 5 Review Pipeline) ─────────────────────────────

def get_pipeline_context(job, user):
    """Build column-wise application data and allowed transitions for the job pipeline."""
    from applications.models import Application
    from applications.services import ALLOWED_TRANSITIONS

    applications = list(
        job.applications.select_related(
            "applicant",
            "applicant__applicant_profile",
        ).prefetch_related("interviews").order_by("-applied_at")
    )

    columns_config = [
        {"id": Application.Status.SUBMITTED, "label": "Applied", "color": "var(--color-primary-color)"},
        {"id": Application.Status.UNDER_REVIEW, "label": "Reviewing", "color": "hsl(38, 92%, 50%)"},
        {"id": Application.Status.SHORTLISTED, "label": "Shortlisted", "color": "hsl(248, 85%, 65%)"},
        {"id": Application.Status.INTERVIEW_SCHEDULED, "label": "Interview", "color": "hsl(174, 80%, 45%)"},
        {"id": Application.Status.OFFER_EXTENDED, "label": "Offer", "color": "hsl(145, 75%, 45%)"},
        {"id": Application.Status.HIRED, "label": "Hired", "color": "hsl(145, 80%, 40%)"},
        {"id": Application.Status.REJECTED, "label": "Rejected", "color": "hsl(354, 75%, 55%)"},
    ]

    board_columns = []
    for col in columns_config:
        col_apps = [a for a in applications if a.status == col["id"]]
        for a in col_apps:
            a.allowed_transitions_list = [
                {"id": s, "label": dict(Application.Status.choices).get(s, s)}
                for s in ALLOWED_TRANSITIONS.get(a.status, [])
            ]
        board_columns.append({
            "id": col["id"],
            "label": col["label"],
            "color": col["color"],
            "applications": col_apps,
            "count": len(col_apps),
        })

    return {
        "job": job,
        "columns": board_columns,
        "total_applications": len(applications),
    }


@login_required
def job_pipeline(request, slug):
    """View applications pipeline for a specific job."""
    _ensure_employer(request.user)
    job = get_object_or_404(Job, slug=slug)

    if job.employer != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to view applications for this job.")

    context = get_pipeline_context(job, request.user)

    if request.headers.get("HX-Request") and request.GET.get("board_only"):
        return render(request, "jobs/partials/pipeline_board.html", context)

    return render(request, "jobs/pipeline.html", context)

