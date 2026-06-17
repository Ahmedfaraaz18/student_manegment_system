import random

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Timetable
from subjects.models import Subject
from teachers.models import Teacher


@api_view(["POST"])
def generate_timetable(request):

    department_id = request.data["department"]

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = ["9-10", "10-11", "11-12", "1-2", "2-3"]

    subjects = list(Subject.objects.filter(department_id=department_id))
    teachers = Teacher.objects.filter(department_id=department_id)

    if not subjects:
        return Response({"message": "No subjects found for this department"}, status=400)

    if not teachers.exists():
        return Response({"message": "No teachers found for this department"}, status=400)

    Timetable.objects.filter(department_id=department_id).delete()

    for day in days:
        for slot in slots:
            subject = random.choice(subjects)
            teacher = teachers.filter(id=subject.teacher_id).first() or random.choice(list(teachers))

            Timetable.objects.create(
                department_id=department_id,
                subject=subject,
                teacher=teacher,
                day=day,
                time_slot=slot
            )

    return Response({"message": "Timetable generated"})
