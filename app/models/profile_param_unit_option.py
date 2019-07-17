import logging

from django.db import models

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

    # def save(self, *args, **kwargs):
    #     try:
    #         unit_opt = ProfileParamUnitOption.objects.get(param_default=True, parameter=self.parameter)
    #         unit_opt.param_default = False
    #         unit_opt.save()
    #     except UnitOption.DoesNotExist:
    #         self.param_default = True
    #     super(UnitOption, self).save(*args, **kwargs)

    @classmethod
    def get_for_profile_parameter(cls, profile, parameter):
        try:
            return cls.objects.get(profile=profile, parameter=parameter)
        except cls.DoesNotExist:
            logging.error(f'ProfileParamUnitOption not exist for {parameter}')
        except cls.MultipleObjectsReturned:
            logging.error(f'ProfileParamUnitOption multiple records for {parameter}')
        return UnitOption.get_default_for_param(parameter)
