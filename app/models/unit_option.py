from django.db import models
from .parameter import Parameter


class UnitOption(models.Model):
    """ Represents a non-default unit of measurement for a parameter, e.g. lb for body mass """
    name = models.CharField(
        max_length=100,
        help_text='Label e.g. pounds'
    )
    symbol = models.CharField(
        max_length=8,
        help_text='Label e.g. lb'
    )
    conversion_factor = models.FloatField(
        max_length=10,
        help_text='Enables conversion to and from the default unit of measurement; can be negative'
    )

    parameter = models.ForeignKey(
        Parameter,
        related_name='unit_choices',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Unit Option: {self.name}'
