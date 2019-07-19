from collections import namedtuple
import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from .managers.datapoint_manager import DatapointManager
from .profile_param_unit_option import ProfileParamUnitOption

log = logging.getLogger(__name__)


class DataPoint(models.Model):

    value = models.FloatField(
        max_length=5,
    )
    value2 = models.FloatField(
        max_length=5,
        help_text='For handling cases e.g. blood pressure two values -- diastolic and systolic bp',
        null=True,
        blank=True,
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
        'app.Parameter',
        on_delete=models.CASCADE,
        related_name='parameters',
    )
    profile = models.ForeignKey(
        'app.Profile',
        on_delete=models.CASCADE,
        related_name='user_datapoints',
    )
    objects = DatapointManager()

    class Meta:
        ordering = ('date', )

    def __str__(self):
        return f'{self.profile} {self.parameter} at {self.date}'

    def save(self, *args, **kwargs):
        try:
            ProfileParamUnitOption.get_unit_option(self.profile, self.parameter)
        except ProfileParamUnitOption.DoesNotExist as e:
            log.error(e)
            raise ValidationError(f'ProfileParamUnitOption does not exist for {self.profile} -- {self.parameter}')
        super(DataPoint, self).save(*args, **kwargs)

    @classmethod
    def bulk_create_from_csv_upload(cls, valid_data):
        """
        :param valid_data: list of dictionaries each containing all data required to save an instance
        :return: namedtuple (bool, str) indicating whether operation was success, and any error message
        """
        Result = namedtuple('BulkCreateResult', ['success', 'message'])
        for dct in valid_data:
            unique_data = {field: dct[field] for field in ['value', 'date', 'parameter', 'profile']}
            if cls.objects.filter(**unique_data).exists():
                return Result(False, f"{dct['parameter'].name} data on {dct['date']} already exists")
        try:
            cls.objects.bulk_create([cls(**data) for data in valid_data])
        except (ValueError, IntegrityError):
            return Result(False, '')
        return Result(True, '')

