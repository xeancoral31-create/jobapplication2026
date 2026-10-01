"""
inkboard/settings/dev.py — Development configuration for Inkboard.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Console email backend for local inspection
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
