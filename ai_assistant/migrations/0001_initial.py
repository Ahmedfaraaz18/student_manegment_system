from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0009_alter_user_managers"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIChat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role_context", models.CharField(choices=[("student", "Student"), ("teacher", "Teacher"), ("admin", "Admin")], max_length=20)),
                ("message", models.TextField()),
                ("response", models.TextField()),
                ("context_snapshot", models.JSONField(blank=True, default=dict)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("provider", models.CharField(choices=[("openai", "OpenAI"), ("fallback", "Fallback")], default="fallback", max_length=20)),
                ("model_name", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("institution", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="ai_chats", to="accounts.institution")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_chats", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
