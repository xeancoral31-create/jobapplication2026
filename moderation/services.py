"""
moderation/services.py — Service layer for Admin Panel actions and audit logging.
"""
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from moderation.models import AdminAction, AuditLog
from jobs.models import Job

User = get_user_model()


def can_admin_perform_action(admin_user, action):
    """
    Check if admin_user has permission to perform action based on access_level.
    - Superadmins can do everything.
    - Moderators cannot suspend users.
    - Non-admins cannot do anything.
    """
    if not (admin_user and admin_user.is_authenticated):
        return False

    is_admin_or_staff = (
        admin_user.role == User.Role.ADMIN
        or admin_user.is_staff
        or admin_user.is_superuser
    )
    if not is_admin_or_staff:
        return False

    # Check suspension permission
    if action in ["suspend", "suspend_user"]:
        access_level = getattr(admin_user, "access_level", None)
        if access_level == User.AccessLevel.MODERATOR and not admin_user.is_superuser:
            return False
        if access_level == User.AccessLevel.SUPERADMIN or admin_user.is_superuser:
            return True
        if hasattr(admin_user, "is_superadmin") and admin_user.is_superadmin:
            return True
        return False

    return True


def log_admin_action(admin, target_type, target_id, action, object_repr=None, changes=None, ip_address=None):
    """
    Central helper: writes an AdminAction (AuditLog) entry.
    Every admin / moderation action MUST write an AdminAction via this helper.

    Parameters:
      admin: User instance (the administrator/moderator performing the action)
      target_type: str, ContentType, or Model class
      target_id: int/pk of the target entity
      action: str ('suspend', 'reactivate', 'approve', 'reject', 'remove', etc.)
      object_repr: optional string representation of the target object
      changes: optional dict of state changes
      ip_address: optional client IP address string
    """
    # Normalize target_type string and ContentType
    ct = None
    target_type_str = ""

    if isinstance(target_type, ContentType):
        ct = target_type
        target_type_str = target_type.model
    elif isinstance(target_type, type):
        target_type_str = target_type._meta.model_name
        ct = ContentType.objects.get_for_model(target_type)
    elif isinstance(target_type, str):
        target_type_str = target_type.lower().strip()
        # Map common string identifiers to ContentType
        if target_type_str in ["user", "applicant", "accounts.user"]:
            ct = ContentType.objects.get_for_model(User)
            target_type_str = "user"
        elif target_type_str in ["employer", "employerprofile"]:
            from accounts.models import EmployerProfile
            ct = ContentType.objects.get_for_model(EmployerProfile)
            target_type_str = "employer"
        elif target_type_str in ["job", "jobs.job"]:
            ct = ContentType.objects.get_for_model(Job)
            target_type_str = "job"
        else:
            try:
                from django.apps import apps
                for model in apps.get_models():
                    if model._meta.model_name.lower() == target_type_str:
                        ct = ContentType.objects.get_for_model(model)
                        break
            except Exception:
                pass

    # Derive object_repr if missing
    if not object_repr and ct and target_id:
        try:
            model_class = ct.model_class()
            if model_class:
                obj = model_class.objects.filter(pk=target_id).first()
                if obj:
                    object_repr = str(obj)
        except Exception:
            pass

    if not object_repr:
        object_repr = f"{target_type_str.capitalize()} #{target_id}"

    action_entry = AdminAction.objects.create(
        admin=admin,
        actor=admin,
        content_type=ct,
        object_id=target_id,
        target_id=target_id,
        target_type=target_type_str,
        object_repr=object_repr,
        action=action,
        changes=changes or {},
        ip_address=ip_address,
    )
    return action_entry


# Aliases for convenience
record_admin_action = log_admin_action
create_admin_action = log_admin_action


def suspend_user(user, admin, ip_address=None):
    """
    Suspend a user (status=suspended).
    Permission rule: Moderators cannot suspend users; superadmins can do everything.
    """
    if not can_admin_perform_action(admin, "suspend"):
        raise PermissionDenied("Moderators cannot suspend users.")

    with transaction.atomic():
        user.status = User.Status.SUSPENDED
        user.save(update_fields=["status"])

        action = log_admin_action(
            admin=admin,
            target_type="user",
            target_id=user.pk,
            action=AuditLog.Action.SUSPEND,
            object_repr=f"{user.get_full_name() or user.username} ({user.email})",
            changes={"status": [User.Status.ACTIVE, User.Status.SUSPENDED]},
            ip_address=ip_address,
        )
    return action


def reactivate_user(user, admin, ip_address=None):
    """
    Reactivate a suspended user (status=active).
    Both moderators and superadmins can reactivate.
    """
    if not can_admin_perform_action(admin, "reactivate"):
        raise PermissionDenied("You do not have permission to reactivate users.")

    with transaction.atomic():
        old_status = user.status
        user.status = User.Status.ACTIVE
        user.save(update_fields=["status"])

        action = log_admin_action(
            admin=admin,
            target_type="user",
            target_id=user.pk,
            action=AuditLog.Action.REACTIVATE,
            object_repr=f"{user.get_full_name() or user.username} ({user.email})",
            changes={"status": [old_status, User.Status.ACTIVE]},
            ip_address=ip_address,
        )
    return action


def approve_employer(employer_user, admin, ip_address=None):
    """
    Approve an employer (is_verified=True, status=active).
    Both moderators and superadmins can approve employers.
    """
    if not can_admin_perform_action(admin, "approve"):
        raise PermissionDenied("You do not have permission to approve employers.")

    with transaction.atomic():
        old_status = employer_user.status
        employer_user.is_verified = True
        employer_user.status = User.Status.ACTIVE
        employer_user.save()

        profile = getattr(employer_user, "employer_profile", None)
        company_name = profile.company_name if profile else employer_user.username

        action = log_admin_action(
            admin=admin,
            target_type="employer",
            target_id=employer_user.pk,
            action=AuditLog.Action.APPROVE,
            object_repr=f"Employer {company_name} ({employer_user.email})",
            changes={"is_verified": [False, True], "status": [old_status, User.Status.ACTIVE]},
            ip_address=ip_address,
        )
    return action


def reject_employer(employer_user, admin, ip_address=None):
    """
    Reject an employer verification request (status=suspended, is_verified=False).
    Both moderators and superadmins can reject employers.
    """
    if not can_admin_perform_action(admin, "reject"):
        raise PermissionDenied("You do not have permission to reject employers.")

    with transaction.atomic():
        old_status = employer_user.status
        employer_user.is_verified = False
        employer_user.status = User.Status.SUSPENDED
        employer_user.save()

        profile = getattr(employer_user, "employer_profile", None)
        company_name = profile.company_name if profile else employer_user.username

        action = log_admin_action(
            admin=admin,
            target_type="employer",
            target_id=employer_user.pk,
            action=AuditLog.Action.REJECT,
            object_repr=f"Employer {company_name} ({employer_user.email})",
            changes={"is_verified": [False, False], "status": [old_status, User.Status.SUSPENDED]},
            ip_address=ip_address,
        )
    return action


def remove_job(job, admin, ip_address=None):
    """
    Moderate / remove any job (status=removed).
    Both moderators and superadmins can remove jobs.
    """
    if not can_admin_perform_action(admin, "remove"):
        raise PermissionDenied("You do not have permission to moderate jobs.")

    with transaction.atomic():
        old_status = job.status
        job.status = Job.Status.REMOVED
        job.save(update_fields=["status"])

        action = log_admin_action(
            admin=admin,
            target_type="job",
            target_id=job.pk,
            action=AuditLog.Action.REMOVE,
            object_repr=f"Job #{job.pk}: {job.title} ({job.employer.username})",
            changes={"status": [old_status, Job.Status.REMOVED]},
            ip_address=ip_address,
        )
    return action
