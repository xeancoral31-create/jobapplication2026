"""accounts/backends.py — Email-based authentication backend."""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """Authenticate with either email or username + password."""

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        # Accept username or email in either kwarg
        lookup = (email or username or "").strip()
        if not lookup or not password:
            return None

        user = User.objects.filter(
            Q(email__iexact=lookup) | Q(username__iexact=lookup)
        ).order_by("-date_joined").first()

        if user is None:
            # Run the default password hasher to prevent timing attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
