"""accounts/backends.py — Email-based authentication backend."""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """Authenticate with email + password instead of username + password."""

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        # Accept email either in the `email` kwarg or the standard `username` slot
        lookup_email = email or username
        if not lookup_email or not password:
            return None
        try:
            user = User.objects.get(email__iexact=lookup_email)
        except User.DoesNotExist:
            # Run the default password hasher to avoid timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Pick the most recently joined account
            user = User.objects.filter(email__iexact=lookup_email).order_by("-date_joined").first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
