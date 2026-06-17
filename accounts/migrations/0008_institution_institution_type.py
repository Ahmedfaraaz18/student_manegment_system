from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_seed_super_admin"),
    ]

    operations = [
        migrations.AddField(
            model_name="institution",
            name="institution_type",
            field=models.CharField(
                choices=[("college", "College"), ("school", "School")],
                default="college",
                max_length=20,
            ),
        ),
    ]
