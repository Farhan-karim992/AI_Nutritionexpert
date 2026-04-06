from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")

    GOAL_CHOICES = [
        ('lose', 'Lose Weight'),
        ('gain', 'Gain Weight'),
        ('maintain', 'Maintain Weight'),
    ]
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES)

    def __str__(self):
        return self.user.username
