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


CAREER_FIELD_CHOICES = [
    ("it", "Information Technology", "💻"),
    ("healthcare", "Nursing & Healthcare", "🩺"),
    ("education", "Education", "📚"),
    ("engineering", "Engineering", "⚙️"),
    ("business", "Business & Finance", "💼"),
    ("hospitality", "Hospitality & Tourism", "🏨"),
    ("government", "Government & Public Service", "🏛️"),
    ("uniformed", "Uniformed Personnel", "🎖️"),
    ("other", "Other Professional Fields", "🌐"),
]

UNIFORMED_BRANCH_CHOICES = [
    ("army", "Army", "🪖", "Ground defense, combat medicine, communications & logistics"),
    ("navy", "Navy", "⚓", "Maritime defense, fleet engineering & surface operations"),
    ("coast_guard", "Coast Guard", "🚢", "Maritime safety, search and rescue & coastal protection"),
    ("police", "Police", "👮", "Public safety, community policing & criminal investigation"),
]

CAREER_FIELD_POSITIONS = {
    "healthcare": [
        "Registered Nurse (RN)",
        "Clinical Nurse Specialist",
        "ICU Staff Nurse",
        "Emergency Room Nurse",
        "Nurse Practitioner",
        "Medical Laboratory Technologist",
        "Radiologic Technologist",
        "Physical Therapist",
        "Healthcare Administrator",
        "Pharmacist",
    ],
    "it": [
        "Software Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full-Stack Developer",
        "Cloud & DevOps Engineer",
        "Cybersecurity Analyst",
        "Data Scientist / AI Engineer",
        "Systems Administrator",
        "IT Support Specialist",
        "Database Administrator",
    ],
    "education": [
        "High School Teacher",
        "Elementary School Educator",
        "University Lecturer / Professor",
        "Special Education Teacher",
        "Academic Coordinator",
        "Guidance Counselor",
        "Instructional Designer",
        "Curriculum Developer",
    ],
    "engineering": [
        "Civil Engineer",
        "Mechanical Engineer",
        "Electrical Engineer",
        "Structural Design Engineer",
        "Chemical Process Engineer",
        "Industrial Safety Engineer",
        "Environmental Engineer",
        "Project Engineer",
    ],
    "business": [
        "Financial Analyst",
        "Senior Accountant",
        "Business Operations Manager",
        "Human Resources Manager",
        "Marketing Specialist",
        "Corporate Auditor",
        "Product Manager",
        "Sales Account Executive",
    ],
    "hospitality": [
        "Hotel Operations Manager",
        "Executive Chef / Sous Chef",
        "Front Desk Supervisor",
        "Food & Beverage Director",
        "Travel & Tourism Coordinator",
        "Event & Banquet Planner",
        "Resort Manager",
    ],
    "government": [
        "Public Administration Officer",
        "Community & Social Services Specialist",
        "Policy Research Analyst",
        "Urban & Regional Planner",
        "Regulatory Compliance Officer",
        "Civil Service Executive",
    ],
    "uniformed": [
        "Army Tactical Communications Officer",
        "Army Combat Medic Specialist",
        "Naval Surface Warfare Specialist",
        "Marine Propulsion Engineer",
        "Coast Guard Search & Rescue Specialist",
        "Maritime Environmental Protection Inspector",
        "Police Patrol Operations Officer",
        "Police Criminal Investigation Detective",
    ],
    "other": [
        "Corporate Legal Counsel",
        "Commercial Architecture Designer",
        "Supply Chain Specialist",
        "Media & Communications Officer",
    ],
}

SLUG_TO_FIELD = {
    "information-technology": "it",
    "development": "it",
    "nursing-and-healthcare": "healthcare",
    "healthcare": "healthcare",
    "education": "education",
    "engineering": "engineering",
    "business-and-finance": "business",
    "finance": "business",
    "hospitality-and-tourism": "hospitality",
    "government-and-public-service": "government",
    "uniformed-personnel": "uniformed",
    "uniformed-army": "uniformed",
    "uniformed-navy": "uniformed",
    "uniformed-coast-guard": "uniformed",
    "uniformed-police": "uniformed",
    "other-professional-fields": "other",
}


def get_available_positions_for_field(field_or_category=None):
    """Return list of distinct, relevant position titles for a field or category."""
    field_code = ""
    if field_or_category:
        clean = field_or_category.strip().lower()
        field_code = SLUG_TO_FIELD.get(clean, clean)

    positions = []
    if field_code and field_code in CAREER_FIELD_POSITIONS:
        positions.extend(CAREER_FIELD_POSITIONS[field_code])

    # Also dynamically query open jobs matching this field/category for actual titles
    qs = Job.objects.filter(status=Job.Status.OPEN)
    if field_code:
        qs = qs.filter(Q(job_field=field_code) | Q(category__slug__icontains=field_code))
    db_titles = list(qs.values_list("title", flat=True).distinct()[:25])
    for t in db_titles:
        if t and t not in positions:
            positions.append(t)

    if not positions:
        # Generic fallback
        for f_pos in CAREER_FIELD_POSITIONS.values():
            for p in f_pos[:3]:
                if p not in positions:
                    positions.append(p)

    return sorted(positions)


# ── Public Job Views ──────────────────────────────────────────────────────────

def positions_by_field(request):
    """HTMX / AJAX endpoint returning position <option> choices for selected field."""
    field = request.GET.get("field") or request.GET.get("category", "").strip()
    selected_position = request.GET.get("position", "").strip()
    positions = get_available_positions_for_field(field)
    return render(request, "jobs/partials/position_options.html", {
        "positions": positions,
        "selected_position": selected_position,
    })


def job_list(request):
    """Public browse jobs list with career field, position, uniformed branch, department, location, salary filters and HTMX pagination."""
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
            | Q(department__icontains=q)
            | Q(employer__employer_profile__company_name__icontains=q)
            | Q(location__icontains=q)
        )

    # Category / Field filter
    category_slug = request.GET.get("category", "").strip()
    field_param = request.GET.get("field", "").strip()
    effective_field = field_param or (SLUG_TO_FIELD.get(category_slug) if category_slug else "")

    if category_slug:
        if category_slug == "uniformed-personnel":
            qs = qs.filter(Q(job_field="uniformed") | Q(category__slug__startswith="uniformed"))
        elif category_slug in ["uniformed-army", "uniformed-navy", "uniformed-coast-guard", "uniformed-police"]:
            branch_val = category_slug.replace("uniformed-", "").replace("-", "_")
            qs = qs.filter(Q(uniformed_branch=branch_val) | Q(category__slug=category_slug))
        else:
            qs = qs.filter(
                Q(category__slug=category_slug)
                | Q(job_field=SLUG_TO_FIELD.get(category_slug, category_slug))
            )
    elif field_param:
        if field_param == "uniformed":
            qs = qs.filter(Q(job_field="uniformed") | Q(category__slug__startswith="uniformed"))
        else:
            qs = qs.filter(Q(job_field=field_param) | Q(category__slug__icontains=field_param))

    # Uniformed Branch filter
    branch = request.GET.get("branch", "").strip()
    if branch:
        qs = qs.filter(
            Q(uniformed_branch=branch)
            | Q(category__slug=f"uniformed-{branch.replace('_', '-')}")
            | Q(title__icontains=branch)
            | Q(department__icontains=branch)
        )

    # Position filter
    position = request.GET.get("position", "").strip()
    if position:
        qs = qs.filter(Q(title__icontains=position) | Q(description__icontains=position))

    # Department filter
    department = request.GET.get("department", "").strip()
    if department:
        qs = qs.filter(department__icontains=department)

    # Employment Type filter
    job_type = request.GET.get("job_type", "").strip()
    if job_type:
        if job_type in ["contract", "contractual"]:
            qs = qs.filter(Q(job_type="contract") | Q(job_type="contractual"))
        else:
            qs = qs.filter(job_type=job_type)

    # Location
    location = request.GET.get("location", "").strip()
    if location:
        qs = qs.filter(location__icontains=location)

    # Remote toggle
    is_remote = request.GET.get("is_remote")
    if is_remote in ["1", "true", "True", "on"]:
        qs = qs.filter(is_remote=True)

    # Min salary
    min_salary = request.GET.get("min_salary", "").strip()
    if min_salary:
        try:
            val = float(min_salary)
            qs = qs.filter(Q(salary_max__gte=val) | (Q(salary_min__gte=val) & Q(salary_max__isnull=True)))
        except ValueError:
            pass

    paginator = Paginator(qs, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all().order_by("name")
    positions = get_available_positions_for_field(effective_field or category_slug)

    context = {
        "page_obj": page_obj,
        "jobs": page_obj.object_list,
        "categories": categories,
        "career_fields": CAREER_FIELD_CHOICES,
        "uniformed_branches": UNIFORMED_BRANCH_CHOICES,
        "positions": positions,
        "employment_types": [
            ("full_time", "Full-Time"),
            ("part_time", "Part-Time"),
            ("contractual", "Contractual"),
            ("temporary", "Temporary"),
            ("internship", "Internship"),
        ],
        "total_count": paginator.count,
        "selected_category": category_slug,
        "selected_field": field_param,
        "selected_branch": branch,
        "selected_position": position,
        "selected_department": department,
        "selected_job_type": job_type,
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
    """List employer jobs with Department, Category, and Employment Type filters."""
    _ensure_employer(request.user)

    # Status tabs filter
    active_tab = request.GET.get("status", "all").lower()
    dept_filter = request.GET.get("department", "").strip()
    cat_filter = request.GET.get("category", "").strip()
    job_type_filter = request.GET.get("job_type", "").strip()
    q = request.GET.get("q", "").strip()

    # Base query for counts
    base_qs = Job.objects.filter(employer=request.user).exclude(status=Job.Status.REMOVED)

    # Aggregate counts across all non-removed statuses (1 query)
    counts = base_qs.aggregate(
        all_count=Count("id"),
        open_count=Count("id", filter=Q(status=Job.Status.OPEN)),
        draft_count=Count("id", filter=Q(status=Job.Status.DRAFT)),
        closed_count=Count("id", filter=Q(status=Job.Status.CLOSED)),
    )

    qs = (
        base_qs
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

    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(department__icontains=q)
            | Q(location__icontains=q)
            | Q(description__icontains=q)
        )

    if dept_filter:
        qs = qs.filter(department__icontains=dept_filter)

    if cat_filter:
        qs = qs.filter(Q(category__slug=cat_filter) | Q(job_field=cat_filter))

    if job_type_filter:
        if job_type_filter in ["contract", "contractual"]:
            qs = qs.filter(Q(job_type="contract") | Q(job_type="contractual"))
        else:
            qs = qs.filter(job_type=job_type_filter)

    # Distinct departments for filter dropdown
    distinct_departments = (
        Job.objects.filter(employer=request.user)
        .exclude(department="")
        .values_list("department", flat=True)
        .distinct()
    )
    categories = Category.objects.all().order_by("name")

    return render(request, "jobs/manage_list.html", {
        "jobs": qs,
        "active_tab": active_tab,
        "counts": counts,
        "distinct_departments": sorted(list(distinct_departments)),
        "categories": categories,
        "selected_department": dept_filter,
        "selected_category": cat_filter,
        "selected_job_type": job_type_filter,
        "search_query": q,
        "employment_types": [
            ("full_time", "Full-Time"),
            ("part_time", "Part-Time"),
            ("contractual", "Contractual"),
            ("temporary", "Temporary"),
            ("internship", "Internship"),
        ],
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

