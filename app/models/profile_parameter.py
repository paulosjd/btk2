import logging
from collections import namedtuple

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from app.models.unit_option import Parameter, UnitOption
from app.utils.calc_param_ideal import CalcParamIdeal

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
    target_value = models.FloatField(
        max_length=6,
        null=True,
        blank=True
    )

    class Meta:
        # TODO try remove 'unit_option'
        # unique_together = ('parameter', 'unit_option', 'profile')

        unique_together = ('parameter', 'profile')

    def __str__(self):
        return f'{self.profile} - {self.parameter} - unit option'

    def targets(self, parameter_name):
        """ Returns a namedtuple containing saved target, recommended target
        based upon age and gender etc, and color rating to indicate how ideal
        latest measurement for parameter is """
        TargetData = namedtuple('target_data', ['saved', 'ideal'])
        def age_from_birth_years():
            return
        age, gender, height = [getattr(self.profile, a, b) for a, b in [] ]
        # or default...
        ideal = CalcParamIdeal(parameter_name, self.profile).get_ideal()
        return TargetData(self.target_value, ideal)

    @classmethod
    def get_unit_option(cls, profile, parameter):
        try:
            return cls.objects.get(
                profile=profile, parameter=parameter
            ).unit_option
        except cls.DoesNotExist:
            logging.error(f'ProfileParamUnitOption not exist for {parameter}')
        except cls.MultipleObjectsReturned:
            logging.error(f'ProfileParamUnitOpt multiple recs for {parameter}')
        logging.info(f'get unit option returned: {parameter.name}')
        return UnitOption.get_default_for_param(parameter)

    @classmethod
    def null_data_params(cls, profile):
        excl_params = profile.summary_data().values_list('parameter')
        return cls.objects.filter(profile=profile).exclude(
            parameter__in=excl_params).all()



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
