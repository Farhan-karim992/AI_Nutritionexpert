from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    age = models.IntegerField()

    height = models.FloatField(
        help_text="Height in cm"
    )

    weight = models.FloatField(
        help_text="Weight in kg"
    )

    GOAL_CHOICES = [

        ('muscle_gain', 'Muscle Gain'),

        ('weight_loss', 'Weight Loss'),

        ('maintenance', 'Maintenance'),
    ]

    goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES
    )

    def __str__(self):
        return self.user.username