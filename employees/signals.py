from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import EmployeeProfile


@receiver(post_save, sender=User)
def create_employee_profile(instance, created, **_):
    if created:
        EmployeeProfile.objects.get_or_create(user=instance)
