from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_platform_super_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.update_or_create(
        username="superadmin",
        defaults={
            "email": "superadmin@campusflow.local",
            "first_name": "Platform",
            "last_name": "Admin",
            "role": "super_admin",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "institution": None,
            "password": make_password("admin123"),
        },
    )


def remove_platform_super_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username="superadmin", email="superadmin@campusflow.local").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_alter_user_managers_institution_created_by_and_more"),
    ]

    operations = [
        migrations.RunPython(create_platform_super_admin, remove_platform_super_admin),
    ]
