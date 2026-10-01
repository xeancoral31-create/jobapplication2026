"""
core/admin_panel_views.py — Dedicated views for the Inkboard Admin Panel.
Handles:
  1. Main Dashboard (/admin-panel/)
  2. User Management: search by role/status, suspend/reactivate
  3. Employer Verification Queue: approve / reject
  4. Job Moderation: remove any job
  5. Audit Log page: filtered by admin, target_type, date
  6. Access-level permission enforcement (Moderators cannot suspend users; superadmins can do everything)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from jobs.models import Job, Category
from moderation.models import AdminAction, AuditLog
from moderation.services import (
    can_admin_perform_action,
    suspend_user,
    reactivate_user,
    approve_employer,
    reject_employer,
    remove_job,
    log_admin_action,
)
from .services import get_admin_dashboard_data

User = get_user_model()


def get_client_ip(request):
    """Safely extract remote client IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def check_admin_access(user):
    """Ensure user is an active Admin, Staff, or Superadmin."""
    if not (user and user.is_authenticated):
        raise PermissionDenied("Authentication required.")

    is_authorized = (
        user.role == User.Role.ADMIN
        or user.is_staff
        or user.is_superuser
    )
    if not is_authorized:
        raise PermissionDenied("Admin panel access requires Administrator privileges.")


# ── 1. Main Admin Dashboard ──────────────────────────────────────────────────

@login_required
def admin_panel_dashboard(request):
    """Main overview dashboard with stats, pending approvals, recent actions, and shortcuts."""
    check_admin_access(request.user)

    ctx = get_admin_dashboard_data(request.user)
    ctx["can_suspend"] = can_admin_perform_action(request.user, "suspend")
    ctx["active_tab"] = "overview"

    # Add recent jobs for quick moderation
    ctx["recent_jobs"] = (
        Job.objects.select_related("employer", "employer__employer_profile", "category")
        .order_by("-created_at")[:6]
    )

    return render(request, "admin_panel/dashboard.html", ctx)


# ── 2. User Management ───────────────────────────────────────────────────────

@login_required
def admin_user_list(request):
    """
    Search and filter platform users by role and status.
    Supports query ?q=..., ?role=..., ?status=...
    """
    check_admin_access(request.user)

    q = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "").strip()
    status_filter = request.GET.get("status", "").strip()

    users_qs = User.objects.all().select_related("employer_profile", "applicant_profile").order_by("-date_joined")

    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(employer_profile__company_name__icontains=q)
        )

    if role_filter and role_filter in [r.value for r in User.Role]:
        users_qs = users_qs.filter(role=role_filter)

    if status_filter and status_filter in [s.value for s in User.Status]:
        users_qs = users_qs.filter(status=status_filter)

    paginator = Paginator(users_qs, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    can_suspend = can_admin_perform_action(request.user, "suspend")

    ctx = {
        "page_obj": page_obj,
        "users": page_obj.object_list,
        "q": q,
        "role_filter": role_filter,
        "status_filter": status_filter,
        "role_choices": User.Role.choices,
        "status_choices": User.Status.choices,
        "total_count": paginator.count,
        "can_suspend": can_suspend,
        "active_tab": "users",
    }
    return render(request, "admin_panel/users.html", ctx)


@login_required
@require_POST
def admin_user_suspend(request, pk):
    """
    Suspend a user account.
    Moderators cannot suspend users; superadmins can do everything.
    """
    check_admin_access(request.user)
    target_user = get_object_or_404(User, pk=pk)

    try:
        suspend_user(target_user, request.user, ip_address=get_client_ip(request))
        messages.success(request, f"User '{target_user.username}' has been successfully suspended.")
    except PermissionDenied as e:
        raise e

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "core:admin_users"
    return redirect(next_url)


@login_required
@require_POST
def admin_user_reactivate(request, pk):
    """
    Reactivate a suspended user account.
    Both moderators and superadmins can reactivate.
    """
    check_admin_access(request.user)
    target_user = get_object_or_404(User, pk=pk)

    reactivate_user(target_user, request.user, ip_address=get_client_ip(request))
    messages.success(request, f"User '{target_user.username}' has been reactivated.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "core:admin_users"
    return redirect(next_url)


# ── 3. Employer Verification Queue ───────────────────────────────────────────

@login_required
def admin_verification_queue(request):
    """Verification queue for pending employer accounts."""
    check_admin_access(request.user)

    q = request.GET.get("q", "").strip()
    pending_qs = (
        User.objects.filter(role=User.Role.EMPLOYER, status=User.Status.PENDING)
        .select_related("employer_profile")
        .order_by("-date_joined")
    )

    if q:
        pending_qs = pending_qs.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(employer_profile__company_name__icontains=q)
        )

    verified_recent = (
        User.objects.filter(role=User.Role.EMPLOYER, status=User.Status.ACTIVE)
        .select_related("employer_profile")
        .order_by("-updated_at")[:8]
    )

    ctx = {
        "pending_employers": pending_qs,
        "pending_count": pending_qs.count(),
        "verified_recent": verified_recent,
        "q": q,
        "active_tab": "verifications",
    }
    return render(request, "admin_panel/verifications.html", ctx)


@login_required
@require_POST
def admin_employer_approve(request, pk):
    """Approve an employer (is_verified=True, status=active)."""
    check_admin_access(request.user)
    employer_user = get_object_or_404(User, pk=pk, role=User.Role.EMPLOYER)

    approve_employer(employer_user, request.user, ip_address=get_client_ip(request))
    messages.success(request, f"Employer '{employer_user.username}' has been approved and verified.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "core:admin_verifications"
    return redirect(next_url)


@login_required
@require_POST
def admin_employer_reject(request, pk):
    """Reject an employer registration."""
    check_admin_access(request.user)
    employer_user = get_object_or_404(User, pk=pk, role=User.Role.EMPLOYER)

    reject_employer(employer_user, request.user, ip_address=get_client_ip(request))
    messages.warning(request, f"Employer '{employer_user.username}' verification has been rejected.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "core:admin_verifications"
    return redirect(next_url)


# ── 4. Job Moderation ────────────────────────────────────────────────────────

@login_required
def admin_job_list(request):
    """Moderation list of all job postings with search and filters."""
    check_admin_access(request.user)

    q = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    category_id = request.GET.get("category", "").strip()

    jobs_qs = Job.objects.all().select_related("employer", "employer__employer_profile", "category").order_by("-created_at")

    if q:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=q)
            | Q(location__icontains=q)
            | Q(employer__username__icontains=q)
            | Q(employer__employer_profile__company_name__icontains=q)
        )

    if status_filter and status_filter in [s.value for s in Job.Status]:
        jobs_qs = jobs_qs.filter(status=status_filter)

    if category_id:
        jobs_qs = jobs_qs.filter(category_id=category_id)

    paginator = Paginator(jobs_qs, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    ctx = {
        "page_obj": page_obj,
        "jobs": page_obj.object_list,
        "q": q,
        "status_filter": status_filter,
        "category_id": category_id,
        "categories": Category.objects.all(),
        "status_choices": Job.Status.choices,
        "total_count": paginator.count,
        "active_tab": "jobs",
    }
    return render(request, "admin_panel/jobs.html", ctx)


@login_required
@require_POST
def admin_job_remove(request, pk):
    """Remove / take down any job listing (status=removed)."""
    check_admin_access(request.user)
    job = get_object_or_404(Job, pk=pk)

    remove_job(job, request.user, ip_address=get_client_ip(request))
    messages.success(request, f"Job '{job.title}' was successfully removed by moderation.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "core:admin_jobs"
    return redirect(next_url)


# ── 5. Audit Log Page ────────────────────────────────────────────────────────

@login_required
def admin_audit_log(request):
    """
    Platform audit log filtered by:
      - admin (actor/admin user ID or username)
      - target_type (user, employer, job, etc.)
      - date (YYYY-MM-DD or date range)
    """
    check_admin_access(request.user)

    admin_filter = request.GET.get("admin", "").strip()
    target_type_filter = request.GET.get("target_type", "").strip()
    date_filter = request.GET.get("date", "").strip()
    action_filter = request.GET.get("action", "").strip()

    logs_qs = AdminAction.objects.select_related("actor", "admin", "content_type").order_by("-timestamp")

    # Filter by admin / actor
    if admin_filter:
        if admin_filter.isdigit():
            logs_qs = logs_qs.filter(Q(admin_id=int(admin_filter)) | Q(actor_id=int(admin_filter)))
        else:
            logs_qs = logs_qs.filter(
                Q(admin__username__iexact=admin_filter)
                | Q(actor__username__iexact=admin_filter)
            )

    # Filter by target_type
    if target_type_filter:
        logs_qs = logs_qs.filter(
            Q(target_type__iexact=target_type_filter)
            | Q(content_type__model__iexact=target_type_filter)
        )

    # Filter by date
    if date_filter:
        parsed_dt = parse_date(date_filter)
        if parsed_dt:
            logs_qs = logs_qs.filter(timestamp__date=parsed_dt)

    # Optional filter by action
    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)

    paginator = Paginator(logs_qs, 25)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Distinct administrators for filter dropdown
    admin_users = User.objects.filter(
        Q(role=User.Role.ADMIN) | Q(is_staff=True) | Q(is_superuser=True)
    ).order_by("username")

    ctx = {
        "page_obj": page_obj,
        "logs": page_obj.object_list,
        "admin_filter": admin_filter,
        "target_type_filter": target_type_filter,
        "date_filter": date_filter,
        "action_filter": action_filter,
        "admin_users": admin_users,
        "target_types": ["user", "employer", "job"],
        "action_choices": AuditLog.Action.choices,
        "total_count": paginator.count,
        "active_tab": "audit",
    }
    return render(request, "admin_panel/audit_log.html", ctx)
