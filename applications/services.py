"""applications/services.py — Candidate pipeline business logic & transitions."""
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from .models import Application, Interview


ALLOWED_TRANSITIONS = {
    Application.Status.SUBMITTED: [
        Application.Status.UNDER_REVIEW,
        Application.Status.SHORTLISTED,
        Application.Status.REJECTED,
    ],
    Application.Status.UNDER_REVIEW: [
        Application.Status.SHORTLISTED,
        Application.Status.INTERVIEW_SCHEDULED,
        Application.Status.REJECTED,
    ],
    Application.Status.SHORTLISTED: [
        Application.Status.INTERVIEW_SCHEDULED,
        Application.Status.OFFER_EXTENDED,
        Application.Status.REJECTED,
        Application.Status.UNDER_REVIEW,
    ],
    Application.Status.INTERVIEW_SCHEDULED: [
        Application.Status.OFFER_EXTENDED,
        Application.Status.SHORTLISTED,
        Application.Status.REJECTED,
    ],
    Application.Status.OFFER_EXTENDED: [
        Application.Status.HIRED,
        Application.Status.REJECTED,
    ],
    Application.Status.HIRED: [],  # terminal
    Application.Status.REJECTED: [
        Application.Status.UNDER_REVIEW,  # allow reopening candidate
    ],
    Application.Status.WITHDRAWN: [],  # terminal
}


def transition_application_status(application, new_status, user):
    """Enforce ownership and valid transitions for an application card.

    Raises:
        PermissionDenied: If user is not the job's employer (or staff).
        ValidationError: If the requested transition is not permitted.
    """
    if not user.is_authenticated or (application.job.employer != user and not user.is_staff):
        raise PermissionDenied("Only the job's employer can move cards.")

    allowed = ALLOWED_TRANSITIONS.get(application.status, [])
    if new_status not in allowed:
        current_display = application.get_status_display()
        target_display = dict(Application.Status.choices).get(new_status, new_status)
        raise ValidationError(
            f"Invalid transition from '{current_display}' to '{target_display}'."
        )

    old_status = application.status
    old_display = application.get_status_display()
    application.status = new_status
    application.save(update_fields=["status", "updated_at"])

    # Send console email on status change
    send_status_change_email(application, old_display)

    return application


def schedule_interview(
    application,
    scheduled_at,
    mode,
    user,
    duration_minutes=45,
    meeting_link="",
    notes="",
    location="",
):
    """Schedule an interview and automatically transition the application to 'interview_scheduled'.

    Raises:
        PermissionDenied: If user is not the job's employer (or staff).
    """
    if not user.is_authenticated or (application.job.employer != user and not user.is_staff):
        raise PermissionDenied("Only the job's employer can schedule interviews.")

    interview = Interview.objects.create(
        application=application,
        scheduled_at=scheduled_at,
        format=mode,
        duration_minutes=duration_minutes or 45,
        meeting_link=meeting_link or "",
        interviewer_notes=notes or "",
        location=location or "",
        outcome=Interview.Outcome.PENDING,
    )

    # Creating an interview moves the application to "interview" (interview_scheduled)
    if application.status != Application.Status.INTERVIEW_SCHEDULED:
        application.status = Application.Status.INTERVIEW_SCHEDULED
        application.save(update_fields=["status", "updated_at"])
        send_status_change_email(application, "Previous Stage")

    # Send console email for interview scheduled
    send_interview_scheduled_email(interview)

    return interview


def record_interview_result(interview, outcome, notes, user):
    """Record result (outcome and feedback notes) for an interview slot.

    Raises:
        PermissionDenied: If user is not the job's employer (or staff).
    """
    application = interview.application
    if not user.is_authenticated or (application.job.employer != user and not user.is_staff):
        raise PermissionDenied("Only the job's employer can record interview results.")

    interview.outcome = outcome
    if notes is not None:
        interview.interviewer_notes = notes
    interview.save(update_fields=["outcome", "interviewer_notes"])

    return interview


def send_status_change_email(application, old_status_display):
    """Send console notification email to applicant regarding application status update."""
    applicant = application.applicant
    job = application.job
    company_name = (
        job.employer.employer_profile.company_name
        if hasattr(job.employer, "employer_profile")
        else job.employer.get_full_name()
    )

    subject = f"[Inkboard] Application Status Update: {job.title}"
    message = (
        f"Hello {applicant.first_name or applicant.username},\n\n"
        f"Your application for '{job.title}' at {company_name} has moved to: {application.get_status_display()}.\n\n"
        f"Log in to your Inkboard candidate dashboard to track your application timeline:\n"
        f"/applications/{application.pk}/\n\n"
        f"Best regards,\nThe Inkboard Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@inkboard.dev"),
            recipient_list=[applicant.email],
            fail_silently=True,
        )
    except Exception:
        pass


def send_interview_scheduled_email(interview):
    """Send console notification email to applicant when an interview is booked."""
    application = interview.application
    applicant = application.applicant
    job = application.job
    company_name = (
        job.employer.employer_profile.company_name
        if hasattr(job.employer, "employer_profile")
        else job.employer.get_full_name()
    )

    date_str = interview.scheduled_at.strftime("%A, %B %d, %Y at %I:%M %p UTC")
    mode_display = interview.get_format_display()

    subject = f"[Inkboard] Interview Scheduled: {job.title}"
    message = (
        f"Hello {applicant.first_name or applicant.username},\n\n"
        f"Great news! {company_name} has scheduled an interview for the '{job.title}' position.\n\n"
        f"Details:\n"
        f"  • Date & Time: {date_str}\n"
        f"  • Mode: {mode_display}\n"
        f"  • Duration: {interview.duration_minutes} minutes\n"
    )

    if interview.meeting_link:
        message += f"  • Link: {interview.meeting_link}\n"
    if interview.location:
        message += f"  • Location: {interview.location}\n"
    if interview.notes:
        message += f"\nPreparation Notes:\n{interview.notes}\n"

    message += (
        f"\nYou can see your upcoming interview pass directly on your applicant dashboard.\n\n"
        f"Best regards,\nThe Inkboard Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@inkboard.dev"),
            recipient_list=[applicant.email],
            fail_silently=True,
        )
    except Exception:
        pass
