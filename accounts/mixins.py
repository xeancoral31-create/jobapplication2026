"""accounts/mixins.py — Role-based and suspension access-control mixins."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Restrict a class-based view to users with a specific role (or roles).

    Usage::

        class MyView(RoleRequiredMixin, View):
            required_roles = ["employer"]          # single role
            # required_roles = ["employer", "admin"]  # multiple
    """

    required_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_roles and request.user.role not in self.required_roles:
            raise PermissionDenied(
                f"This area is restricted to: {', '.join(self.required_roles)}."
            )
        return super().dispatch(request, *args, **kwargs)


class SuspensionMixin:
    """
    Block suspended users from accessing any view that inherits this mixin.
    Returns a 403 with a clear message.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_suspended:
            return render(
                request,
                "403.html",
                {
                    "reason": "suspended",
                    "title": "Account Suspended",
                    "message": (
                        "Your account has been suspended. "
                        "Please contact support at support@inkboard.dev."
                    ),
                },
                status=403,
            )
        return super().dispatch(request, *args, **kwargs)


class EmployerRequiredMixin(RoleRequiredMixin, SuspensionMixin):
    required_roles = ["employer"]


class ApplicantRequiredMixin(RoleRequiredMixin, SuspensionMixin):
    required_roles = ["applicant"]


class AdminRequiredMixin(RoleRequiredMixin, SuspensionMixin):
    required_roles = ["admin"]
