import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from jobs.models import Job
from .forms import ApplicationForm
from .models import Application, Interview
from .services import (
    transition_application_status,
    schedule_interview,
    record_interview_result,
    ALLOWED_TRANSITIONS,
)


def get_status_timeline(application):
    """Generate ordered steps with state (completed/current/upcoming/terminal)."""
    current_status = application.status

    if current_status == Application.Status.REJECTED:
        return [
            {
                "key": "submitted",
                "title": "Application Submitted",
                "desc": f"Received on {application.applied_at.strftime('%b %d, %Y')}.",
                "state": "completed",
            },
            {
                "key": "under_review",
                "title": "Under Review",
                "desc": "Reviewed by hiring committee.",
                "state": "completed",
            },
            {
                "key": "rejected",
                "title": "Application Not Selected",
                "desc": "The hiring team decided to move forward with other candidates at this time.",
                "state": "terminal-danger",
            },
        ]

    if current_status == Application.Status.WITHDRAWN:
        withdrawn_date = (
            application.withdrawn_at.strftime("%b %d, %Y")
            if application.withdrawn_at
            else "record"
        )
        return [
            {
                "key": "submitted",
                "title": "Application Submitted",
                "desc": f"Received on {application.applied_at.strftime('%b %d, %Y')}.",
                "state": "completed",
            },
            {
                "key": "withdrawn",
                "title": "Application Withdrawn",
                "desc": f"Withdrawn by candidate on {withdrawn_date}.",
                "state": "terminal-neutral",
            },
        ]

    stages = [
        ("submitted", "Application Submitted", "Your submission is securely registered in the employer's inbox."),
        ("under_review", "Under Review", "Hiring team is evaluating your portfolio, resume, and qualifications."),
        ("shortlisted", "Shortlisted", "Your profile stood out and has been added to the interview shortlist."),
        ("interview_scheduled", "Interview Scheduled", "Live interview conversations or technical assessments active."),
        ("offer_extended", "Offer Extended", "An official offer package has been prepared for you."),
        ("hired", "Hired", "Offer accepted. Welcome to the company!"),
    ]

    stage_keys = [s[0] for s in stages]
    try:
        current_idx = stage_keys.index(current_status)
    except ValueError:
        current_idx = 0

    steps = []
    for i, (key, title, desc) in enumerate(stages):
        if i < current_idx:
            state = "completed"
        elif i == current_idx:
            state = "current"
        else:
            state = "upcoming"

        steps.append({
            "key": key,
            "title": title,
            "desc": desc,
            "state": state,
            "is_current": (i == current_idx),
            "is_completed": (i <= current_idx),
        })

    return steps


@login_required
def apply(request, job_id):
    """Submit an application for a specific open job listing."""
    # Only applicants are permitted to apply
    if request.user.role != User.Role.APPLICANT:
        raise PermissionDenied("Only applicant accounts can apply to job listings.")

    job = get_object_or_404(
        Job.objects.select_related("employer", "employer__employer_profile", "category"),
        pk=job_id,
    )

    # Validate that job is open and deadline is not in the past
    today = timezone.now().date()
    if not job.is_open() or (job.deadline and job.deadline < today):
        return render(
            request,
            "applications/job_closed.html",
            {"job": job},
            status=400,
        )

    # Check for friendly already-applied state before rendering form
    existing_app = Application.objects.filter(applicant=request.user, job=job).first()
    if existing_app:
        return render(
            request,
            "applications/already_applied.html",
            {"job": job, "application": existing_app},
        )

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    application = form.save(commit=False)
                    application.applicant = request.user
                    application.job = job
                    application.status = Application.Status.SUBMITTED

                    # Resume snapshot logic
                    if request.FILES.get("resume"):
                        application.resume_snapshot = request.FILES["resume"]
                    elif hasattr(request.user, "applicant_profile") and request.user.applicant_profile.resume:
                        application.resume_snapshot = request.user.applicant_profile.resume

                    application.save()
                    messages.success(request, f"Application for '{job.title}' submitted successfully!")
                    return redirect("applications:detail", pk=application.pk)

            except IntegrityError:
                # In case of race conditions or double submission, catch unique constraint
                existing_app = Application.objects.filter(applicant=request.user, job=job).first()
                messages.info(request, "You have already submitted an application for this position.")
                return render(
                    request,
                    "applications/already_applied.html",
                    {"job": job, "application": existing_app},
                )
    else:
        form = ApplicationForm(user=request.user)

    return render(
        request,
        "applications/apply.html",
        {
            "job": job,
            "form": form,
            "has_profile_resume": bool(
                hasattr(request.user, "applicant_profile") and request.user.applicant_profile.resume
            ),
        },
    )


@login_required
def my_applications(request):
    """Applicant's dashboard listing of all their submitted applications with status stamps."""
    if request.user.role != User.Role.APPLICANT:
        raise PermissionDenied("Only applicant accounts can access candidate applications.")

    qs = (
        Application.objects.filter(applicant=request.user)
        .select_related("job", "job__employer", "job__employer__employer_profile", "job__category")
        .order_by("-applied_at")
    )

    status_filter = request.GET.get("status", "all")
    if status_filter == "active":
        qs = qs.filter(
            status__in=[
                Application.Status.SUBMITTED,
                Application.Status.UNDER_REVIEW,
                Application.Status.SHORTLISTED,
                Application.Status.INTERVIEW_SCHEDULED,
            ]
        )
    elif status_filter == "decided":
        qs = qs.filter(
            status__in=[
                Application.Status.OFFER_EXTENDED,
                Application.Status.HIRED,
                Application.Status.REJECTED,
                Application.Status.WITHDRAWN,
            ]
        )

    all_apps = Application.objects.filter(applicant=request.user)
    counts = {
        "all": all_apps.count(),
        "active": all_apps.filter(
            status__in=[
                Application.Status.SUBMITTED,
                Application.Status.UNDER_REVIEW,
                Application.Status.SHORTLISTED,
                Application.Status.INTERVIEW_SCHEDULED,
            ]
        ).count(),
        "decided": all_apps.filter(
            status__in=[
                Application.Status.OFFER_EXTENDED,
                Application.Status.HIRED,
                Application.Status.REJECTED,
                Application.Status.WITHDRAWN,
            ]
        ).count(),
    }

    return render(
        request,
        "applications/list.html",
        {
            "applications": qs,
            "current_status": status_filter,
            "counts": counts,
        },
    )


@login_required
def application_detail(request, pk):
    """View application details and status progression timeline."""
    app = get_object_or_404(
        Application.objects.select_related(
            "job",
            "job__employer",
            "job__employer__employer_profile",
            "job__category",
            "applicant",
        ),
        pk=pk,
    )

    # Permission: only the applicant, the job's employer, or staff can view
    if not (app.applicant == request.user or app.job.employer == request.user or request.user.is_staff):
        raise PermissionDenied("You do not have permission to view this application.")

    timeline = get_status_timeline(app)

    return render(
        request,
        "applications/detail.html",
        {
            "application": app,
            "timeline": timeline,
            "is_applicant": bool(request.user == app.applicant),
        },
    )


@login_required
def withdraw(request, pk):
    """Allow an applicant to withdraw their active application."""
    app = get_object_or_404(Application, pk=pk, applicant=request.user)

    if request.method == "POST":
        if app.status not in [Application.Status.HIRED, Application.Status.WITHDRAWN]:
            app.status = Application.Status.WITHDRAWN
            app.withdrawn_at = timezone.now()
            app.save(update_fields=["status", "withdrawn_at", "updated_at"])
            messages.info(request, f"Your application for '{app.job.title}' has been withdrawn.")
        return redirect("applications:detail", pk=app.pk)

    return render(request, "applications/withdraw.html", {"application": app})


# ── Pipeline Review & Management (Stage 5) ───────────────────────────────────

@login_required
def application_transition(request, pk):
    """HTMX endpoint to move an application card to an allowed new status."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    application = get_object_or_404(
        Application.objects.select_related("job", "job__employer", "applicant"),
        pk=pk,
    )
    new_status = request.POST.get("new_status")
    if not new_status:
        return HttpResponseBadRequest("Missing new_status parameter.")

    try:
        transition_application_status(application, new_status, request.user)
    except PermissionDenied as e:
        raise e
    except ValidationError as e:
        return HttpResponseBadRequest(str(e.message if hasattr(e, "message") else e))

    if request.headers.get("HX-Request"):
        from jobs.views import get_pipeline_context
        context = get_pipeline_context(application.job, request.user)
        return render(request, "jobs/partials/pipeline_board.html", context)

    messages.success(request, f"Candidate moved to {application.get_status_display()}.")
    return redirect("jobs:pipeline", slug=application.job.slug)


@login_required
def application_drawer(request, pk):
    """HTMX endpoint returning the candidate review slide-over drawer."""
    application = get_object_or_404(
        Application.objects.select_related(
            "job",
            "job__employer",
            "job__category",
            "applicant",
            "applicant__applicant_profile",
        ),
        pk=pk,
    )

    if application.job.employer != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to review this candidate.")

    allowed = [
        {"id": s, "label": dict(Application.Status.choices).get(s, s)}
        for s in ALLOWED_TRANSITIONS.get(application.status, [])
    ]
    interviews = application.interviews.all().order_by("-scheduled_at")

    return render(
        request,
        "applications/partials/drawer.html",
        {
            "application": application,
            "applicant": application.applicant,
            "profile": getattr(application.applicant, "applicant_profile", None),
            "allowed_transitions": allowed,
            "interviews": interviews,
            "interview_formats": Interview.Format.choices,
            "interview_outcomes": Interview.Outcome.choices,
            "now": timezone.now(),
        },
    )


@login_required
def schedule_interview_view(request, pk):
    """Schedule an interview and move the application to 'interview_scheduled'."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    application = get_object_or_404(
        Application.objects.select_related("job", "job__employer", "applicant"),
        pk=pk,
    )

    scheduled_at_raw = request.POST.get("scheduled_at")
    mode = request.POST.get("mode") or Interview.Format.VIDEO
    duration = int(request.POST.get("duration_minutes") or 45)
    meeting_link = request.POST.get("meeting_link", "").strip()
    location = request.POST.get("location", "").strip()
    notes = request.POST.get("notes", "").strip()

    if not scheduled_at_raw:
        return HttpResponseBadRequest("Scheduled date and time are required.")

    try:
        from django.utils.dateparse import parse_datetime
        scheduled_at = parse_datetime(scheduled_at_raw)
        if not scheduled_at:
            import datetime
            scheduled_at = datetime.datetime.fromisoformat(scheduled_at_raw)
        if timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(scheduled_at)
    except Exception:
        return HttpResponseBadRequest("Invalid date format.")

    interview = schedule_interview(
        application=application,
        scheduled_at=scheduled_at,
        mode=mode,
        user=request.user,
        duration_minutes=duration,
        meeting_link=meeting_link,
        location=location,
        notes=notes,
    )

    if request.headers.get("HX-Request"):
        from jobs.views import get_pipeline_context
        context = get_pipeline_context(application.job, request.user)
        response = render(request, "jobs/partials/pipeline_board.html", context)
        response["HX-Trigger"] = "interviewScheduled"
        return response

    messages.success(request, f"Interview scheduled for {application.applicant.get_full_name()}.")
    return redirect("jobs:pipeline", slug=application.job.slug)


@login_required
def record_interview_result_view(request, pk):
    """HTMX endpoint for employer to record interview outcome and feedback notes."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    interview = get_object_or_404(
        Interview.objects.select_related("application", "application__job"),
        pk=pk,
    )
    outcome = request.POST.get("outcome") or Interview.Outcome.PASSED
    notes = request.POST.get("notes", "").strip()

    record_interview_result(
        interview=interview,
        outcome=outcome,
        notes=notes,
        user=request.user,
    )

    if request.headers.get("HX-Request"):
        return application_drawer(request, pk=interview.application.pk)

    messages.success(request, "Interview outcome recorded successfully.")
    return redirect("jobs:pipeline", slug=interview.application.job.slug)


@login_required
def download_resume(request, pk):
    """
    Secure resume download:
    Accessible only by:
      - The owning applicant
      - The job's employer
      - Platform administrators
    """
    application = get_object_or_404(
        Application.objects.select_related("applicant", "job", "job__employer"),
        pk=pk,
    )
    user = request.user

    is_owner = (application.applicant == user)
    is_employer = (application.job.employer == user)
    is_admin = (user.role == User.Role.ADMIN or user.is_staff or user.is_superuser)

    if not (is_owner or is_employer or is_admin):
        raise PermissionDenied("You do not have permission to view or download this resume.")

    if not application.resume_snapshot:
        raise Http404("No resume attached to this application.")

    filename = os.path.basename(application.resume_snapshot.name)
    return FileResponse(application.resume_snapshot.open(), as_attachment=True, filename=filename)


