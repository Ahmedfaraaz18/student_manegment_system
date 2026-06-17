from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .serializers import DEFAULT_PASSWORD
from .models import Student

User = get_user_model()


@receiver(post_save, sender=Student)
def create_student_login(sender, instance, created, **kwargs):
    if not created or instance.user_id:
        return

    base_username = (
        (instance.email or "").strip().lower()
        or f"student{instance.id}"
    )
    username = base_username
    counter = 1
    while User.all_objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    user = User(
        username=username,
        email=instance.email or "",
        role=User.STUDENT,
        institution=instance.institution,
        first_name=instance.name,
    )
    user.set_password(DEFAULT_PASSWORD)
    user.save()

    Student.objects.filter(pk=instance.pk).update(user=user)
