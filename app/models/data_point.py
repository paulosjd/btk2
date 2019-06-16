from django.db import models
from .parameter import Parameter
from .profile import Profile


class DataPoint(models.Model):

    value = models.FloatField(
        max_length=5,
    )
    qualifier = models.CharField(
        help_text='Noteworthy influences on a measurement value',
        max_length=50,
        blank=True,
        null=True,
    )
    date = models.DateField(
        help_text='Date of measurement'
    )
    time = models.TimeField(
        help_text='Optional time of measurement; can be influential',
        blank=True,
        null=True,
    )
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name='parameters',
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='user_datapoints',
    )
    # objects = SubTopicManager()

    def __str__(self):
        return f'{self.profile} {self.parameter} at {self.date}'
