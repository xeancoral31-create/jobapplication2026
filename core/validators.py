"""
core/validators.py — File upload and input validation utilities.
"""
import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_RESUME_SIZE_BYTES = 30 * 1024 * 1024  # 30 MB
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}


def validate_resume_file(file):
    """
    Validate that an uploaded resume:
      1. Has an allowed file extension (.pdf, .doc, .docx)
      2. Does not exceed 30 MB in size
    """
    if not file:
        return

    # Check file size
    file_size = getattr(file, "size", None)
    if file_size and file_size > MAX_RESUME_SIZE_BYTES:
        max_mb = MAX_RESUME_SIZE_BYTES // (1024 * 1024)
        raise ValidationError(
            _(f"Resume file size must not exceed {max_mb} MB. Uploaded file is {file_size / (1024 * 1024):.1f} MB.")
        )

    # Check file extension
    file_name = getattr(file, "name", "")
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        allowed = ", ".join(ext.upper().lstrip(".") for ext in sorted(ALLOWED_RESUME_EXTENSIONS))
        raise ValidationError(
            _(f"Invalid file format '{ext}'. Only {allowed} files are accepted.")
        )
