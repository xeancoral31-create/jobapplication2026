"""accounts/signals.py - Auto-create profile on user save."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, EmployerProfile, ApplicantProfile


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    """Create the matching profile model when a new user is created."""
    if not created:
        return
    if instance.role == User.Role.EMPLOYER:
        EmployerProfile.objects.get_or_create(user=instance)
    elif instance.role == User.Role.APPLICANT:
        ApplicantProfile.objects.get_or_create(user=instance)
