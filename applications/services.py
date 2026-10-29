"""applications/services.py — Candidate pipeline business logic & transitions."""
import datetime
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _

from .models import Application, Interview, Offer


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
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.UNDER_REVIEW,
    ],
    Application.Status.INTERVIEW_SCHEDULED: [
        Application.Status.OFFER_EXTENDED,
        Application.Status.HIRED,
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


def create_hire_notification(application):
    """Deliver an in-system notification immediately to the applicant's account with start date and message."""
    from core.models import Notification

    applicant = application.applicant
    job = application.job
    company_name = (
        job.employer.employer_profile.company_name
        if hasattr(job.employer, "employer_profile") and job.employer.employer_profile.company_name
        else job.employer.get_full_name() or job.employer.username
    )

    formatted_date = (
        application.start_date.strftime("%B %d, %Y")
        if application.start_date
        else "Confirmed upon onboarding"
    )

    description = (
        f"Congratulations {applicant.first_name or applicant.username}! "
        f"{company_name} has officially confirmed your hire for {job.title}.\n\n"
        f"📅 Official Work Start Date: {formatted_date}\n\n"
        f"💬 Message from Employer:\n{application.hire_message}"
    )

    detail_url = reverse("applications:detail", kwargs={"pk": application.pk})

    return Notification.objects.create(
        user=applicant,
        kind=Notification.Kind.APPLICATION,
        message=f"🎉 You have been hired for {job.title}!",
        highlight=f"Start Date: {formatted_date}",
        detail_title=f"Offer Accepted & Official Start Date — {job.title}",
        description=description,
        status_label="Official Hire",
        pills=[company_name, f"Starts: {formatted_date}", "Hired"],
        action_url=detail_url,
        action_text="View Confirmed Start Date",
        is_read=False,
        created_at=timezone.now(),
    )


def transition_application_status(
    application,
    new_status,
    user,
    hire_message="",
    start_date=None,
):
    """Enforce ownership and valid transitions for an application card.

    When moving to HIRED, employer must provide:
      - start_date: Official work start date (required)
      - hire_message: Message to the candidate (required)

    Raises:
        PermissionDenied: If user is not the job's employer (or staff).
        ValidationError: If the requested transition is not permitted or hire fields are missing.
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

    # Validate mandatory hire details when transitioning to HIRED
    if new_status == Application.Status.HIRED:
        if not start_date:
            raise ValidationError("The applicant's official work start date is required when hiring.")

        parsed_start_date = None
        if isinstance(start_date, (datetime.date, datetime.datetime)):
            parsed_start_date = start_date.date() if isinstance(start_date, datetime.datetime) else start_date
        elif isinstance(start_date, str):
            clean_date_str = start_date.strip()
            if not clean_date_str:
                raise ValidationError("The applicant's official work start date is required when hiring.")
            parsed_start_date = parse_date(clean_date_str)
            if not parsed_start_date:
                try:
                    parsed_start_date = datetime.date.fromisoformat(clean_date_str)
                except ValueError:
                    raise ValidationError("Please provide a valid official work start date (YYYY-MM-DD).")
        else:
            raise ValidationError("Please provide a valid official work start date.")

        if not hire_message or not str(hire_message).strip():
            raise ValidationError("A message to the applicant is required when hiring.")

        clean_hire_message = str(hire_message).strip()

        old_status = application.status
        old_display = application.get_status_display()
        application.status = new_status
        application.start_date = parsed_start_date
        application.hire_message = clean_hire_message
        application.hired_at = timezone.now()
        application.save(update_fields=["status", "start_date", "hire_message", "hired_at", "updated_at"])

        # Sync with Offer if present
        if hasattr(application, "offer"):
            offer = application.offer
            offer.start_date = parsed_start_date
            offer.status = Offer.OfferStatus.ACCEPTED
            if not offer.notes:
                offer.notes = clean_hire_message
            offer.save(update_fields=["start_date", "status", "notes", "updated_at"])

        # Immediately deliver notification to applicant's account
        create_hire_notification(application)

        # Send status change email
        send_status_change_email(application, old_display)

        return application

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

    if application.status == Application.Status.HIRED:
        subject = f"[WorkWise] Congratulations! You're Hired for {job.title}"
        formatted_date = (
            application.start_date.strftime("%A, %B %d, %Y")
            if application.start_date
            else "Confirmed upon onboarding"
        )
        message = (
            f"Hello {applicant.first_name or applicant.username},\n\n"
            f"Great news! You have been officially hired for '{job.title}' at {company_name}.\n\n"
            f"Official Work Start Date:\n"
            f"  • {formatted_date}\n\n"
            f"Message from Employer:\n"
            f"  \"{application.hire_message}\"\n\n"
            f"Log in to your WorkWise candidate dashboard to view your confirmed onboarding details:\n"
            f"/applications/{application.pk}/\n\n"
            f"Best regards,\nThe WorkWise Team"
        )
    else:
        subject = f"[WorkWise] Application Status Update: {job.title}"
        message = (
            f"Hello {applicant.first_name or applicant.username},\n\n"
            f"Your application for '{job.title}' at {company_name} has moved to: {application.get_status_display()}.\n\n"
            f"Log in to your WorkWise candidate dashboard to track your application timeline:\n"
            f"/applications/{application.pk}/\n\n"
            f"Best regards,\nThe WorkWise Team"
        )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@workwise.dev"),
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

    subject = f"[WorkWise] Interview Scheduled: {job.title}"
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
        f"Best regards,\nThe WorkWise Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@workwise.dev"),
            recipient_list=[applicant.email],
            fail_silently=True,
        )
    except Exception:
        pass
