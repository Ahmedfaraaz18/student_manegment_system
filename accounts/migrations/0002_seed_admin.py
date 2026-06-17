from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.update_or_create(
        username="admin",
        defaults={
            "email": "admin@eduerp.local",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "password": make_password("admin123"),
        },
    )


def remove_default_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username="admin", email="admin@eduerp.local").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]
