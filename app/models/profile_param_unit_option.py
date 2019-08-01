import logging

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from app.models.unit_option import UnitOption


log = logging.getLogger(__name__)


class ProfileParamUnitOption(models.Model):
    parameter = models.ForeignKey(
        'app.Parameter',
        on_delete=models.CASCADE,
    )
    unit_option = models.ForeignKey(
        'app.UnitOption',
        on_delete=models.CASCADE,
    )
    profile = models.ForeignKey(
        'app.Profile',
        related_name='param_unit_options',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('parameter', 'unit_option', 'profile')

    def __str__(self):
        return f'{self.profile} - {self.parameter} - unit option'

    @classmethod
    def get_unit_option(cls, profile, parameter):
        try:
            return cls.objects.get(
                profile=profile, parameter=parameter
            ).unit_option
        except cls.DoesNotExist:
            logging.error(f'ProfileParamUnitOption not exist for {parameter}')
        except cls.MultipleObjectsReturned:
            logging.error(f'ProfileParamUnitOption multiple records for {parameter}')
        logging.info(f'get unit option returned: {parameter.name}')
        return UnitOption.get_default_for_param(parameter)


@receiver(post_delete)
def profile_param_unit_option_post_delete(sender, instance, *args, **kwargs):
    """ To clean up any redundant model instances, e.g. no DataPoint instances
    pointing to a Parameter that such a model
     points to. Note that as sender argument not included in the decorator,
     this callback is called for all models """
    from app.models.data_point import DataPoint
    if sender == DataPoint:
        filter_kwargs = dict(profile=instance.profile,
                             parameter=instance.parameter)
        if not DataPoint.objects.filter(**filter_kwargs).exists():
            for obj in ProfileParamUnitOption.objects.filter(**filter_kwargs):
                obj.delete()
