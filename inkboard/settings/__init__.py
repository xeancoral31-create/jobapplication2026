"""
inkboard/settings/__init__.py — Environment-aware settings loader.
Defaults to dev settings unless DJANGO_ENV is set to 'prod' or 'production'.
"""
import os

env = os.environ.get("DJANGO_ENV", "dev").lower()

if env in ["prod", "production"]:
    from .prod import *
else:
    from .dev import *
