from django.db import models
from departments.models import Department
from subjects.models import Subject
from teachers.models import Teacher


class Timetable(models.Model):

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    day = models.CharField(max_length=20)

    time_slot = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.department} - {self.subject} - {self.day}"
