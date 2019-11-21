from collections import namedtuple
import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, models

from .profile_parameter import ProfileParamUnitOption

log = logging.getLogger(__name__)


class DataPoint(models.Model):

    value = models.FloatField(
        max_length=6,
    )
    value2 = models.FloatField(
        max_length=6,
        help_text='For handling cases e.g. blood pressure two values -- '
                  'diastolic and systolic bp',
        null=True,
        blank=True,
    )
    date = models.DateField(
        help_text='Date of measurement'
    )
    qualifier = models.CharField(
        max_length=50,
        help_text='Qualifying notes e.g. time of day',
        null=True,
        blank=True,
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

    class Meta:
        unique_together = ('date', 'parameter', 'profile')
        ordering = ('date', )

    def __str__(self):
        return f'{self.profile} {self.parameter} at {self.date}'

    def save(self, *args, **kwargs):
        if not all([self.profile, self.parameter]):
            raise IntegrityError
        try:
            ProfileParamUnitOption.get_unit_option(self.profile, self.parameter)
        except ObjectDoesNotExist as e:
            log.error(e)
            raise ValidationError('ProfileParamUnitOption does not exist')
        super(DataPoint, self).save(*args, **kwargs)

    @classmethod
    def bulk_create_from_csv_upload(cls, valid_data):
        """
        :param valid_data: list of dictionaries each containing all data
        required to save an instance
        :return: namedtuple (bool, str) indicating whether operation was
        success, and any error message
        """
        Result = namedtuple('BulkCreateResult', ['success', 'message'])
        for dct in valid_data:
            unique_data = {field: dct[field] for field in
                           ['value', 'date', 'parameter', 'profile']}
            if cls.objects.filter(**unique_data).exists():
                return Result(False, f"{dct['parameter'].name} "
                                     f"data on {dct['date']} already exists")
        try:
            cls.objects.bulk_create([cls(**data) for data in valid_data])
        except (ValueError, IntegrityError) as e:
            log.error(e)
            return Result(False, '')
        return Result(True, '')

    @classmethod
    def update_on_date_match_or_create(cls, **kwargs):
        uc_fields = ['parameter', 'profile', 'date']
        try:
            record = cls.objects.filter(
                **{k: kwargs[k] for k in kwargs if k in uc_fields}
            ).first()
        except KeyError as e:
            log.error(e)
            return
        if not record:
            fields = uc_fields + kwargs['parameter'].upload_fields.split(', ')
            try:
                cls.objects.create(
                    **{k: v for k, v in kwargs.items() if k in fields}
                )
            except (ValidationError, IntegrityError) as e:
                log.error(e)
                return
        else:
            for k, v in kwargs.items():
                setattr(record, k, v)
            record.save()

    @classmethod
    def create_demo_profile_data(cls, profile):
        cls.objects.filter(profile__user__name='demo').update(profile=profile)
