import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from django.db import connection

tables = [
    "announcements_announcement",
    "attendance_attendance",
    "departments_academicunit",
    "departments_department",
    "exams_exam",
    "exams_examtype",
    "exams_marks",
    "placements_company",
    "placements_placement",
    "results_result",
    "students_student",
    "subjects_subject",
    "teachers_teacher",
    "accounts_user",
    "accounts_user_groups",
    "accounts_user_user_permissions",
    "institutions_institution",
    "timetable_timetable",
]

with connection.cursor() as cursor:
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')

print("dropped custom tables")
