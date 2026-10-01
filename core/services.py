"""core/services.py — Dashboard data aggregation services.

Each service function handles a single role dashboard with optimized
queries (aggregate/annotate/select_related) to strictly prevent N+1 queries.
"""
import datetime
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import User
from jobs.models import Job
from applications.models import Application, Interview
from moderation.models import AuditLog, Flag, AdminAction


def get_employer_dashboard_data(employer_user):
    """Compute and return all dashboard metrics and datasets for an Employer.

    Metrics:
      - open_jobs: open job postings by this employer
      - total_jobs: all job postings by this employer
      - total_applications: total applications across all jobs of this employer
      - shortlisted: applications in SHORTLISTED status
      - interviews_next_7_days: interviews scheduled in [now, now + 7 days]
      - recent_applications: 10 most recent applications with select_related
      - my_jobs: jobs with annotated applicant_count
      - is_verified: boolean, False if employer account is awaiting approval
    """
    now = timezone.now()
    next_7_days = now + datetime.timedelta(days=7)

    # 1. Job aggregates for this employer (1 query)
    job_stats = Job.objects.filter(employer=employer_user).aggregate(
        total_jobs=Count("id"),
        open_jobs=Count("id", filter=Q(status=Job.Status.OPEN)),
    )
    open_jobs = job_stats["open_jobs"] or 0
    total_jobs = job_stats["total_jobs"] or 0

    # 2. Application aggregates for this employer's jobs (1 query)
    app_stats = Application.objects.filter(job__employer=employer_user).aggregate(
        total_applications=Count("id"),
        shortlisted=Count("id", filter=Q(status=Application.Status.SHORTLISTED)),
        under_review=Count("id", filter=Q(status=Application.Status.UNDER_REVIEW)),
        hired=Count("id", filter=Q(status=Application.Status.HIRED)),
    )
    total_applications = app_stats["total_applications"] or 0
    shortlisted = app_stats["shortlisted"] or 0

    # 3. Interviews in next 7 days (1 query)
    interviews_next_7_days = Interview.objects.filter(
        application__job__employer=employer_user,
        scheduled_at__gte=now,
        scheduled_at__lte=next_7_days,
    ).count()

    # 4. Recent applications table (select_related prevents N+1)
    recent_applications = (
        Application.objects.filter(job__employer=employer_user)
        .select_related("applicant", "applicant__applicant_profile", "job")
        .order_by("-applied_at")[:10]
    )

    # 5. Employer jobs annotated with applicant count (1 query, no N+1)
    my_jobs = (
        Job.objects.filter(employer=employer_user)
        .annotate(applicant_count=Count("applications"))
        .order_by("-created_at")[:10]
    )

    # 6. Verification status
    is_verified = getattr(employer_user, "is_verified", employer_user.status == User.Status.ACTIVE)

    return {
        "open_jobs": open_jobs,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "shortlisted": shortlisted,
        "interviews_next_7_days": interviews_next_7_days,
        "recent_applications": recent_applications,
        "my_jobs": my_jobs,
        "is_verified": is_verified,
        "is_pending": not is_verified,
    }


def calculate_profile_completeness(user):
    """Calculate profile completeness percentage (0 to 100) and missing items."""
    score = 0
    missing = []

    # Basic user information (25%)
    if user.first_name and user.last_name:
        score += 15
    else:
        missing.append("Add your full name (+15%)")

    if user.avatar:
        score += 10
    else:
        missing.append("Upload a profile picture (+10%)")

    # Bio & location (15%)
    if user.bio:
        score += 10
    else:
        missing.append("Write a brief bio (+10%)")

    if user.location:
        score += 5
    else:
        missing.append("Add your location (+5%)")

    # Applicant profile specific (60%)
    profile = getattr(user, "applicant_profile", None)
    if profile:
        if profile.headline:
            score += 20
        else:
            missing.append("Add a professional headline (+20%)")

        if profile.skills:
            score += 15
        else:
            missing.append("List your skills (+15%)")

        if profile.resume:
            score += 15
        else:
            missing.append("Upload your resume (+15%)")

        if profile.linkedin_url or profile.github_url or profile.portfolio_url:
            score += 10
        else:
            missing.append("Add portfolio / LinkedIn / GitHub links (+10%)")
    else:
        missing.append("Complete applicant profile (+60%)")

    return min(score, 100), missing


def get_applicant_dashboard_data(applicant_user):
    """Compute and return all dashboard metrics and datasets for an Applicant.

    Metrics:
      - applications_by_status: counts grouped by status via aggregate
      - upcoming_interviews: scheduled interviews (now & future) as ticket cards
      - recent_applications: recent applications with stamp chips
      - profile_completeness: completeness percentage & missing items
      - recommended_jobs: open job postings excluding ones already applied to
    """
    now = timezone.now()

    # 1. Applications by status aggregated in a single query
    status_stats = Application.objects.filter(applicant=applicant_user).aggregate(
        total=Count("id"),
        submitted=Count("id", filter=Q(status=Application.Status.SUBMITTED)),
        under_review=Count("id", filter=Q(status=Application.Status.UNDER_REVIEW)),
        shortlisted=Count("id", filter=Q(status=Application.Status.SHORTLISTED)),
        interview_scheduled=Count("id", filter=Q(status=Application.Status.INTERVIEW_SCHEDULED)),
        offer_extended=Count("id", filter=Q(status=Application.Status.OFFER_EXTENDED)),
        hired=Count("id", filter=Q(status=Application.Status.HIRED)),
        rejected=Count("id", filter=Q(status=Application.Status.REJECTED)),
        withdrawn=Count("id", filter=Q(status=Application.Status.WITHDRAWN)),
    )
    total_applications = status_stats["total"] or 0

    applications_by_status = {
        Application.Status.SUBMITTED: status_stats["submitted"] or 0,
        Application.Status.UNDER_REVIEW: status_stats["under_review"] or 0,
        Application.Status.SHORTLISTED: status_stats["shortlisted"] or 0,
        Application.Status.INTERVIEW_SCHEDULED: status_stats["interview_scheduled"] or 0,
        Application.Status.OFFER_EXTENDED: status_stats["offer_extended"] or 0,
        Application.Status.HIRED: status_stats["hired"] or 0,
        Application.Status.REJECTED: status_stats["rejected"] or 0,
        Application.Status.WITHDRAWN: status_stats["withdrawn"] or 0,
    }

    # Clean list of non-zero or highlighted statuses for UI breakdown
    status_breakdown = [
        {"status": "submitted", "label": "Submitted", "count": status_stats["submitted"] or 0, "badge": "badge--submitted"},
        {"status": "under_review", "label": "Under Review", "count": status_stats["under_review"] or 0, "badge": "badge--under_review"},
        {"status": "shortlisted", "label": "Shortlisted", "count": status_stats["shortlisted"] or 0, "badge": "badge--shortlisted"},
        {"status": "interview_scheduled", "label": "Interview", "count": status_stats["interview_scheduled"] or 0, "badge": "badge--accent"},
        {"status": "offer_extended", "label": "Offer Extended", "count": status_stats["offer_extended"] or 0, "badge": "badge--success"},
        {"status": "hired", "label": "Hired", "count": status_stats["hired"] or 0, "badge": "badge--success"},
        {"status": "rejected", "label": "Rejected", "count": status_stats["rejected"] or 0, "badge": "badge--danger"},
        {"status": "withdrawn", "label": "Withdrawn", "count": status_stats["withdrawn"] or 0, "badge": "badge--neutral"},
    ]

    active_count = (
        (status_stats["submitted"] or 0)
        + (status_stats["under_review"] or 0)
        + (status_stats["shortlisted"] or 0)
        + (status_stats["interview_scheduled"] or 0)
        + (status_stats["offer_extended"] or 0)
    )

    # 2. Upcoming interviews (ticket cards) with select_related
    upcoming_interviews = (
        Interview.objects.filter(
            application__applicant=applicant_user,
            scheduled_at__gte=now,
        )
        .select_related(
            "application",
            "application__job",
            "application__job__employer",
            "application__job__employer__employer_profile",
        )
        .order_by("scheduled_at")[:6]
    )

    # 3. Recent applications (with stamp chips) with select_related
    recent_applications = (
        Application.objects.filter(applicant=applicant_user)
        .select_related(
            "job",
            "job__employer",
            "job__employer__employer_profile",
            "job__category",
        )
        .order_by("-applied_at")[:10]
    )

    # 4. Profile completeness
    profile_completeness, missing_profile_steps = calculate_profile_completeness(applicant_user)

    # 5. Recommended jobs
    recommended = (
        Job.objects.filter(status=Job.Status.OPEN)
        .exclude(applications__applicant=applicant_user)
        .select_related("employer", "employer__employer_profile", "category")[:6]
    )

    return {
        "total_applications": total_applications,
        "active_applications": active_count,
        "applications_by_status": applications_by_status,
        "status_stats": status_stats,
        "status_breakdown": status_breakdown,
        "upcoming_interviews": upcoming_interviews,
        "recent_applications": recent_applications,
        "profile_completeness": profile_completeness,
        "missing_profile_steps": missing_profile_steps,
        "recommended": recommended,
    }


def get_admin_dashboard_data(admin_user=None):
    """Compute and return all dashboard metrics and datasets for Site Admins.

    Metrics:
      - users_by_role: counts by role via aggregate
      - employers_awaiting_verification: count and list of pending employers
      - open_jobs: count of open jobs across platform
      - recent AdminAction rows: recent AuditLog/AdminAction entries
      - open_flags: pending moderation flags
    """
    # 1. Users by role (1 query)
    user_stats = User.objects.aggregate(
        total_users=Count("id"),
        applicants=Count("id", filter=Q(role=User.Role.APPLICANT)),
        employers=Count("id", filter=Q(role=User.Role.EMPLOYER)),
        admins=Count("id", filter=Q(role=User.Role.ADMIN)),
    )
    total_users = user_stats["total_users"] or 0
    applicants_count = user_stats["applicants"] or 0
    employers_count = user_stats["employers"] or 0
    admins_count = user_stats["admins"] or 0

    users_by_role = {
        User.Role.APPLICANT: applicants_count,
        User.Role.EMPLOYER: employers_count,
        User.Role.ADMIN: admins_count,
    }

    users_by_role_list = [
        {"role": "applicant", "label": "Job Seekers", "count": applicants_count, "color": "var(--color-accent-400)"},
        {"role": "employer", "label": "Employers", "count": employers_count, "color": "hsl(354 70% 54%)"},
        {"role": "admin", "label": "Administrators", "count": admins_count, "color": "hsl(270 60% 55%)"},
    ]

    # 2. Employers awaiting verification (pending approval)
    employers_awaiting_verification = User.objects.filter(
        role=User.Role.EMPLOYER,
        status=User.Status.PENDING,
    ).count()

    pending_employers = (
        User.objects.filter(role=User.Role.EMPLOYER, status=User.Status.PENDING)
        .select_related("employer_profile")
        .order_by("-date_joined")[:6]
    )

    # 3. Open jobs
    job_stats = Job.objects.aggregate(
        total_jobs=Count("id"),
        open_jobs=Count("id", filter=Q(status=Job.Status.OPEN)),
    )
    open_jobs = job_stats["open_jobs"] or 0
    total_jobs = job_stats["total_jobs"] or 0

    # 4. Recent AdminAction (AuditLog) rows (select_related actor, content_type)
    recent_admin_actions = (
        AdminAction.objects.select_related("actor", "content_type")
        .order_by("-timestamp")[:10]
    )

    # 5. Open moderation flags
    open_flags = Flag.objects.filter(status=Flag.FlagStatus.OPEN).count()

    # 6. Recently joined users
    recent_users = User.objects.order_by("-date_joined")[:8]

    return {
        "user_stats": user_stats,
        "users_by_role": users_by_role,
        "users_by_role_list": users_by_role_list,
        "total_users": total_users,
        "applicants_count": applicants_count,
        "employers_count": employers_count,
        "admins_count": admins_count,
        "employers_awaiting_verification": employers_awaiting_verification,
        "pending_employers": pending_employers,
        "open_jobs": open_jobs,
        "total_jobs": total_jobs,
        "recent_admin_actions": recent_admin_actions,
        "open_flags": open_flags,
        "recent_users": recent_users,
    }
