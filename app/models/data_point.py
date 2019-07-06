from collections import namedtuple
from django.db import IntegrityError, models

from .parameter import Parameter
from .profile import Profile


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

    @classmethod
    def bulk_create_from_csv_upload(cls, valid_data):
        """
        :param valid_data: list of dictionaries each containing all data required to save an instance
        :return: namedtuple (bool, str) indicating whether operation was success, and any error message
        """
        Result = namedtuple('BulkCreateResult', ['success', 'message'])
        for dct in valid_data:
            unique_data = {field: dct[field] for field in ['value', 'date', 'parameter']}
            if cls.objects.filter(**unique_data).exists():
                return Result(False, f"{dct['parameter'].name} data on {dct['date']} already exists")
        try:
            cls.objects.bulk_create([cls(**data) for data in valid_data])
        except (ValueError, IntegrityError):
            return Result(False, '')
        return Result(True, '')
