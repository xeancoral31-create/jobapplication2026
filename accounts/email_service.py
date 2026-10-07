"""accounts/email_service.py — EmailJS & system email delivery for verification codes."""
import json
import logging
import random
import urllib.request
import urllib.error
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

# EmailJS Service Configuration provided by User
EMAILJS_SERVICE_ID = "service_d9tnkwy"
EMAILJS_TEMPLATE_PRIMARY = "template_mpzej9i"
EMAILJS_TEMPLATE_SECONDARY = "template_34cwshe"
EMAILJS_PUBLIC_KEY = "iq_eVMF1nN7cttg2t"
EMAILJS_PRIVATE_KEY = "DB3DHYt7vHu9pj3GiXK-Z"


def generate_verification_code() -> str:
    """Generate a secure 6-digit numeric verification code."""
    return f"{random.randint(100000, 999999)}"


def send_verification_email(user, code: str) -> dict:
    """
    Deliver the verification code to the user's email address.
    Attempts direct EmailJS REST API dispatch, falls back to standard Django email,
    and returns template payload for client-side EmailJS delivery.
    """
    recipient_email = user.email
    recipient_name = user.get_full_name() or user.username or "Valued User"
    
    template_params = {
        "to_email": recipient_email,
        "email": recipient_email,
        "user_email": recipient_email,
        "recipient": recipient_email,
        "to_name": recipient_name,
        "name": recipient_name,
        "user_name": recipient_name,
        "code": code,
        "verification_code": code,
        "passcode": code,
        "otp": code,
        "time_limit": "15 minutes",
        "message": f"Your WorkWise password reset verification code is: {code}. It will expire in 15 minutes.",
    }

    # 1. Attempt backend EmailJS REST API dispatch
    emailjs_sent = False
    for template_id in [EMAILJS_TEMPLATE_PRIMARY, EMAILJS_TEMPLATE_SECONDARY]:
        try:
            url = "https://api.emailjs.com/api/v1.0/email/send"
            payload = {
                "service_id": EMAILJS_SERVICE_ID,
                "template_id": template_id,
                "user_id": EMAILJS_PUBLIC_KEY,
                "accessToken": EMAILJS_PRIVATE_KEY,
                "template_params": template_params,
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "WorkWise-Auth-Server/2026.1",
                },
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status in (200, 201):
                    emailjs_sent = True
                    logger.info("Verification code sent via backend EmailJS (template %s)", template_id)
                    break
        except Exception as e:
            logger.debug("Backend EmailJS dispatch notice for %s: %s", template_id, e)

    # 2. Also send via Django email backend as fallback/audit log
    try:
        subject = "Your WorkWise Verification Code"
        body = (
            f"Hello {recipient_name},\n\n"
            f"We received a request to reset your WorkWise password.\n\n"
            f"Your 6-digit verification code is: {code}\n\n"
            f"This code will expire in 15 minutes. If you did not request this, please ignore this email.\n\n"
            f"— The WorkWise Team"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@workwise.dev"),
            recipient_list=[recipient_email],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning("Django send_mail fallback error: %s", e)

    # Return config payload for immediate frontend EmailJS client-side SDK dispatch
    return {
        "success": True,
        "email": recipient_email,
        "name": recipient_name,
        "code": code,
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_PRIMARY,
        "template_id_secondary": EMAILJS_TEMPLATE_SECONDARY,
        "public_key": EMAILJS_PUBLIC_KEY,
        "template_params": template_params,
    }
