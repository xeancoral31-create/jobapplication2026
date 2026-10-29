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

    # Check file extension first (gives cleaner error for wrong format)
    file_name = getattr(file, "name", "")
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        allowed = ", ".join(e.upper().lstrip(".") for e in sorted(ALLOWED_RESUME_EXTENSIONS))
        raise ValidationError(
            _(f"Invalid file format '{ext}'. Only {allowed} files are accepted.")
        )

    # Check file size (use is not None so that 0-byte files are also evaluated)
    file_size = getattr(file, "size", None)
    if file_size is not None and file_size > MAX_RESUME_SIZE_BYTES:
        max_mb = MAX_RESUME_SIZE_BYTES // (1024 * 1024)
        raise ValidationError(
            _(f"Resume file size must not exceed {max_mb} MB. Uploaded file is {file_size / (1024 * 1024):.1f} MB.")
        )
