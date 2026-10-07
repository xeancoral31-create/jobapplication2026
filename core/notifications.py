"""core/notifications.py — Notification services, context processor, and JSON endpoints."""
import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from .models import Notification

DROPDOWN_LIMIT = 10


# ── Services ───────────────────────────────────────────────────────────────

def ensure_default_notifications(user):
    """Give a user their starter notifications exactly once (first time they have none)."""
    if Notification.objects.filter(user=user).exists():
        return
    now = timezone.now()
    jobs_url = reverse("jobs:list")
    Notification.objects.bulk_create([
        Notification(
            user=user,
            kind=Notification.Kind.JOB,
            message="NovaTech Solutions is hiring:",
            highlight="Frontend Developer",
            detail_title="NovaTech Solutions is hiring: Frontend Developer",
            description=(
                "NovaTech Solutions has published a high-priority opening for a Frontend Developer. "
                "You match key skills in React, TypeScript, modern responsive interfaces, and CSS architecture."
            ),
            status_label="Active Opportunity",
            pills=["NovaTech Solutions", "Full-time • Remote", "$110k – $140k", "React & TypeScript"],
            action_url=jobs_url,
            action_text="View Job Details",
            created_at=now - datetime.timedelta(minutes=10),
        ),
        Notification(
            user=user,
            kind=Notification.Kind.LISTING,
            message="GreenStack Systems published",
            highlight="Backend Developer",
            detail_title="GreenStack Systems published Backend Developer",
            description=(
                "A new backend engineering position has been published by GreenStack Systems. The position "
                "involves building robust Django APIs, scalable database architectures, and cloud services."
            ),
            status_label="Verified Company",
            pills=["GreenStack Systems", "Hybrid • New York", "$125k – $155k", "Python & Django"],
            action_url=jobs_url,
            action_text="Explore Role",
            created_at=now - datetime.timedelta(hours=2),
        ),
        Notification(
            user=user,
            kind=Notification.Kind.PLATFORM,
            message="Welcome to WorkWise! Browse curated roles or post a job.",
            detail_title="Welcome to WorkWise!",
            description=(
                "Welcome to WorkWise! Discover curated tech opportunities, submit applications directly with "
                "customized profiles, or publish and manage company job listings seamlessly."
            ),
            status_label="Platform Onboarding",
            pills=["WorkWise", "Career Hub", "Verified Jobs", "Fast-track Applications"],
            action_url=reverse("core:dashboard"),
            action_text="Open Dashboard",
            is_read=True,
            read_at=now,
            created_at=now - datetime.timedelta(days=1),
        ),
    ])


def unread_queryset(user):
    return Notification.objects.filter(user=user, is_read=False)


def mark_all_read(user):
    """Persist read state for every unread notification of this user. Returns rows updated."""
    return unread_queryset(user).update(is_read=True, read_at=timezone.now())


def _state_payload(user, **extra):
    unread_ids = list(unread_queryset(user).values_list("id", flat=True))
    return {"ok": True, "unread_count": len(unread_ids), "unread_ids": unread_ids, **extra}


# ── Context processor ─────────────────────────────────────────────────────

def notifications_context(request):
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated):
        return {}
    ensure_default_notifications(user)
    return {
        "nav_notifications": list(Notification.objects.filter(user=user)[:DROPDOWN_LIMIT]),
        "unread_notification_count": unread_queryset(user).count(),
    }


# ── JSON endpoints ─────────────────────────────────────────────────────────

def _json_login_required(view):
    """login_required that answers AJAX callers with 401 JSON instead of a redirect."""
    wrapped = login_required(view)

    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "authentication_required"}, status=401)
        return wrapped(request, *args, **kwargs)

    inner.__name__ = view.__name__
    inner.__doc__ = view.__doc__
    return inner


@require_POST
@_json_login_required
def notifications_mark_all_read(request):
    updated = mark_all_read(request.user)
    return JsonResponse(_state_payload(request.user, updated=updated))


@require_POST
@_json_login_required
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_read()
    return JsonResponse(_state_payload(request.user, id=notification.pk))


@never_cache
@require_GET
@_json_login_required
def notifications_state(request):
    """Lightweight sync endpoint: the frontend reconciles its badge/list against this."""
    return JsonResponse(_state_payload(request.user))
