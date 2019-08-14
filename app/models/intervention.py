import logging

from django.db import models

log = logging.getLogger(__name__)


class Intervention(models.Model):

    name = models.CharField(
        max_length=50,
    )
    start_date = models.DateField(
        help_text='Date of measurement'
    )
    end_date = models.DateField(
        help_text='Date of measurement',
        null=True,
        blank=True
    )
    profile = models.ForeignKey(
        'app.Profile',
        on_delete=models.CASCADE,
        related_name='user_datapoints',
    )

    class Meta:
        unique_together = ('name', 'profile')

    def __str__(self):
        return f'{self.name} | {self.profile}'
