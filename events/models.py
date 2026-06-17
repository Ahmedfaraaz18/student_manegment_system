from django.db import models
from institutions.models import Institution


class Event(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    event_date = models.DateField()

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

# Create your models here.
