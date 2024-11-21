from django.db import models
from users.models import User


class Class(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    max_participants = models.IntegerField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer_classes')

    def __str__(self):
        return self.name
