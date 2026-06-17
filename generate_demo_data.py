from institutions.models import Institution
from students.models import Student
from teachers.models import Teacher
from departments.models import AcademicUnit


institution, _ = Institution.objects.get_or_create(
    name="Demo Engineering Institute",
    defaults={
        "email": "demo@institute.edu",
        "phone": "9999999999",
        "institution_type": "engineering",
    },
)

departments = []
for i in range(4):
    dept, _ = AcademicUnit.objects.get_or_create(
        institution=institution,
        code=f"D{i}",
        defaults={"name": f"Dept {i}"},
    )
    departments.append(dept)

for i in range(20):
    Teacher.objects.get_or_create(
        email=f"teacher{i}@demo.edu",
        defaults={
            "name": f"Teacher {i}",
            "institution": institution,
            "department": departments[i % len(departments)],
            "phone": f"900000{i:04d}",
        },
    )

for i in range(200):
    Student.objects.get_or_create(
        first_name="Student",
        last_name=str(i),
        department=departments[i % len(departments)],
        defaults={
            "parent_name": f"Parent {i}",
            "parent_phone": f"800000{i:04d}",
        },
    )
