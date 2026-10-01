"""
core/media_views.py — Protected media access view.
Enforces that sensitive media (such as resumes) is accessible ONLY by:
  1. The owning applicant
  2. The job's employer (for application resumes)
  3. Platform administrators
"""
import os
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.static import serve
from accounts.models import User, ApplicantProfile
from applications.models import Application


@login_required
def protected_media_serve(request, path):
    """
    Serve media files with strict access control:
      - Admins (role=ADMIN, is_staff, is_superuser) can access any media file.
      - Non-resume files (e.g. avatars, logos): accessible to authenticated users.
      - Resume files (resumes/*, application_resumes/*):
          - Allowed for the owning applicant
          - Allowed for the job's employer (for application resumes)
          - Denied for all other users (403 PermissionDenied)
    """
    user = request.user

    # Administrators have universal access
    if user.is_authenticated and (user.role == User.Role.ADMIN or user.is_staff or user.is_superuser):
        return serve(request, path, document_root=settings.MEDIA_ROOT)

    normalized_path = path.replace("\\", "/").strip("/")

    # Check if this is a sensitive resume document
    is_resume = (
        normalized_path.startswith("resumes/")
        or normalized_path.startswith("application_resumes/")
        or "resume" in normalized_path.lower()
    )

    if not is_resume:
        # Non-resume media (avatars, logos) can be served to authenticated users
        return serve(request, path, document_root=settings.MEDIA_ROOT)

    # 1. Profile Resume ownership check
    if normalized_path.startswith("resumes/"):
        filename = normalized_path.split("/")[-1]
        is_owner = ApplicantProfile.objects.filter(
            user=user,
            resume__icontains=filename,
        ).exists()
        if is_owner:
            return serve(request, path, document_root=settings.MEDIA_ROOT)
        raise PermissionDenied("You do not have permission to access this resume.")

    # 2. Application Resume Snapshot ownership check
    if normalized_path.startswith("application_resumes/"):
        filename = normalized_path.split("/")[-1]
        matching_apps = Application.objects.filter(
            resume_snapshot__icontains=filename
        ).select_related("applicant", "job", "job__employer")

        if not matching_apps.exists():
            raise PermissionDenied("You do not have permission to access this resume.")

        is_applicant = any(app.applicant == user for app in matching_apps)
        is_job_employer = any(app.job.employer == user for app in matching_apps)

        if is_applicant or is_job_employer:
            return serve(request, path, document_root=settings.MEDIA_ROOT)

        raise PermissionDenied("You do not have permission to access this candidate's resume.")

    raise PermissionDenied("Access to this document is restricted.")
