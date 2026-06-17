from django.db import migrations


def backfill_default_institution(apps, schema_editor):
    Institution = apps.get_model("accounts", "Institution")
    User = apps.get_model("accounts", "User")
    Department = apps.get_model("departments", "Department")
    Teacher = apps.get_model("teachers", "Teacher")
    Student = apps.get_model("students", "Student")
    Subject = apps.get_model("subjects", "Subject")
    Exam = apps.get_model("exams", "Exam")
    Attendance = apps.get_model("attendance", "Attendance")
    Result = apps.get_model("results", "Result")
    Placement = apps.get_model("placements", "Placement")
    Announcement = apps.get_model("announcements", "Announcement")

    institution, _ = Institution.objects.get_or_create(
        code="default-college",
        defaults={
            "name": "Default College",
            "contact_email": "",
            "phone": "",
            "address": "",
            "is_active": True,
        },
    )

    User.objects.filter(institution__isnull=True).update(institution=institution)
    Department.objects.filter(institution__isnull=True).update(institution=institution)
    Teacher.objects.filter(institution__isnull=True).update(institution=institution)
    Student.objects.filter(institution__isnull=True).update(institution=institution)
    Subject.objects.filter(institution__isnull=True).update(institution=institution)
    Exam.objects.filter(institution__isnull=True).update(institution=institution)
    Attendance.objects.filter(institution__isnull=True).update(institution=institution)
    Result.objects.filter(institution__isnull=True).update(institution=institution)
    Placement.objects.filter(institution__isnull=True).update(institution=institution)
    Announcement.objects.filter(institution__isnull=True).update(institution=institution)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_institution_user_institution"),
        ("announcements", "0002_announcement_institution"),
        ("attendance", "0002_attendance_institution"),
        ("departments", "0002_department_institution_alter_department_name_and_more"),
        ("exams", "0002_exam_institution_alter_exam_unique_together"),
        ("placements", "0002_placement_institution"),
        ("results", "0002_result_institution"),
        ("students", "0002_student_institution"),
        ("subjects", "0002_alter_subject_unique_together_subject_institution_and_more"),
        ("teachers", "0002_teacher_institution"),
    ]

    operations = [
        migrations.RunPython(backfill_default_institution, migrations.RunPython.noop),
    ]
