import logging
from collections import namedtuple

from django.db import models

from app.models.unit_option import UnitOption
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
        related_name='profile_parameters',
        on_delete=models.CASCADE,
    )
    linked_parameter = models.ForeignKey(
        'app.Parameter',
        related_name='profile_parameter_linked_parameters',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target_value = models.FloatField(
        max_length=6,
        null=True,
        blank=True
    )
    target_value2 = models.FloatField(
        max_length=6,
        null=True,
        blank=True
    )
    color_hex = models.CharField(
        max_length=30,
        default='',
        blank=True
    )
    color_range_val_1 = models.IntegerField(
        default=10,
        blank=True
    )
    color_range_val_2 = models.IntegerField(
        default=20,
        blank=True
    )

    class Meta:
        unique_together = ('parameter', 'profile')

    def __str__(self):
        return f'{self.profile} - {self.parameter} - unit option'

    def targets(self, latest_val, latest_val2=None):
        """ Returns a namedtuple containing saved target, recommended target
        based upon age and gender etc, and color rating to indicate how ideal
        latest measurement for parameter is """
        fields = ['saved', 'saved2', 'misc_data', 'required_field', 'ideal',
                  'ideal2', 'ideal_prepend', 'ideal2_prepend']
        TargetData = namedtuple('target_data', fields)
        ideal = CalcParamIdeal(
            self.parameter.name, self.profile, latest_val, latest_val2,
            unit_is_default=self.unit_option.param_default,
            con_factor=self.unit_option.conversion_factor
        )
        ideal_data = ideal.get_ideal_data()
        return TargetData(
            self.target_value, self.target_value2, ideal.misc_data,
            ideal.required_field, *[ideal_data.get(k, '') for k in fields[-4:]]
        )

    @classmethod
    def get_unit_option(cls, profile, parameter):
        try:
            return cls.objects.get(
                profile=profile, parameter=parameter
            ).unit_option
        except cls.DoesNotExist:
            logging.error(f'ProfileParamUnitOption not exist for {parameter}')
        logging.info(f'get unit option returned: {parameter.name}')
        return UnitOption.get_default_for_param(parameter)

    @classmethod
    def null_data_params(cls, profile):
        excl_params = profile.summary_data().values_list('parameter')
        return cls.objects.filter(profile=profile).exclude(
            parameter__in=excl_params).all()

    @staticmethod
    def get_unit_info(obj):
        """
        :param obj: expected to have 'param_name' and 'pp_unit_info' attributes
        :return: dict or None
        """
        if obj.pp_unit_option:
            pp_unit_info = {
                k: getattr(obj.pp_unit_option.unit_option, k)
                for k in ['param_default', 'conversion_factor', 'symbol']
            }
            pp_unit_info['param_name'] = obj.param_name
            pp_unit_info.update({
                k: getattr(obj.pp_unit_option, k) for k in
                ['color_hex', 'color_range_val_1', 'color_range_val_2']
            })
            return pp_unit_info

    @staticmethod
    def param_unit_opt_dct(unit_opt):
        return {f'unit_{field}': getattr(unit_opt, field)
                for field in ['symbol', 'name', 'param_default',
                              'conversion_factor']}
