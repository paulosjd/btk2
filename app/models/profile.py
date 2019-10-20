from datetime import datetime

from django.db import models

from .parameter import Parameter
from .profile_parameter import ProfileParamUnitOption
from .user import User


class Profile(models.Model):
    """ A model representing a User and their activity """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    email_confirmed = models.BooleanField(
        default=False,
    )
    birth_year = models.IntegerField(
        default=0,
    )
    height = models.IntegerField(
        default=0,
        help_text='Height in cm'
    )
    gender = models.CharField(
        choices=[('', ' '), ('m', 'Male'), ('f', 'Female')],
        default='',
        max_length=1
    )

    @property
    def age(self):
        if self.birth_year:
            return datetime.now().year - self.birth_year

    def __str__(self):
        return self.user.username + '_profile'

    def available_parameters(self):
        return Parameter.objects.union(
            Parameter.objects.custom_parameters().filter(profile=self))

    def available_unit(self):
        return Parameter.objects.union(
            Parameter.objects.custom_parameters().filter(profile=self))

    def all_datapoints(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').all()

    def summary_data(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').distinct('parameter')

    def param_unit_options(self):
        return self.unit_options.order_by(
            'parameter').distinct('parameter')

    def all_bookmarks(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').all()

    def get_bookmarks_data(self):
        return [
            {**{field: getattr(obj, field) for field in
             ['id', 'url', 'title', 'parameter_id']},
             **{'param_id': obj.parameter.id,
                'param_name': obj.parameter.name}}
            for obj in self.user_bookmarks.all()
        ]

    def get_linked_profile_parameters(self):
        return [[prm.name for prm in lpp.parameters.all()]
                for lpp in self.linked_profile_parameters.all()]

    @classmethod
    def create_demo_user(cls):
        cls.objects.create(is_temporary=True)

    def get_summary_data(self):
        fields = ['name', 'upload_fields', 'upload_field_labels', 'ideal_info',
                  'ideal_info_url', 'id', 'num_values'] + \
                 [f'value2_short_label_{i}' for i in [1, 2]]
        summary_qs = self.summary_data()
        return [{
            'parameter': {
                **{field: getattr(obj.parameter, field) for field in fields},
                **ProfileParamUnitOption.param_unit_opt_dct(
                    ProfileParamUnitOption.get_unit_option(
                        self, summary_qs[i].parameter)
                )},
            'data_point': {field: getattr(obj, field)
                           for field in ['date', 'value', 'value2']},
        } for i, obj in enumerate(summary_qs)]
