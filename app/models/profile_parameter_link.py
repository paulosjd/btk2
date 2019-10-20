import logging

from django.core.exceptions import ValidationError
from django.db import models

log = logging.getLogger(__name__)


class ProfileParameterLink(models.Model):

    parameters = models.ManyToManyField(
        'app.Parameter',
    )
    profile = models.ForeignKey(
        'app.Profile',
        related_name='linked_profile_parameters',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'ParamLink ({self.id}) for {self.profile}'

    def save(self, *args, **kwargs):
        if self.parameters.count() > 2:
            raise ValidationError('Maximum number of parameters is 2')
        return super().save(*args, **kwargs)
