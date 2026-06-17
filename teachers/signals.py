from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.services.sms_service import send_teacher_credentials

from .serializers import DEFAULT_PASSWORD
from .models import Teacher

User = get_user_model()


@receiver(post_save, sender=Teacher)
def create_teacher_login(sender, instance, created, **kwargs):
    if not created or instance.user_id:
        return

    base_username = (instance.email or "").strip().lower()
    if not base_username:
        base_username = f"teacher{instance.id}"

    username = base_username
    counter = 1
    while User.all_objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    user = User(
        username=username,
        email=instance.email,
        role=User.TEACHER,
        institution=instance.institution,
        first_name=instance.name,
    )
    user.set_password(DEFAULT_PASSWORD)
    user.save()

    Teacher.objects.filter(pk=instance.pk).update(user=user)
    send_teacher_credentials(instance, user.username, DEFAULT_PASSWORD)
