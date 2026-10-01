"""
inkboard/settings/prod.py — Production configuration for Inkboard.
Includes WhiteNoise static compression, secure cookies, and hardened headers.
"""
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS", "inkboard.dev,www.inkboard.dev,localhost,127.0.0.1"
).split(",")

# ── WhiteNoise Compression & Manifest Storage ──────────────────────────────
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ── Production Security & Cookies ──────────────────────────────────────────
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Production Email
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
