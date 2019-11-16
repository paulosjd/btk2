from datetime import datetime
from operator import itemgetter
from typing import List, Optional

from django.db import models

from .managers.profile_manager import ProfileManager
from .profile_parameter import ProfileParamUnitOption
from .user import User


class Profile(models.Model):
    """ A model representing a User. Links to their activity and data. """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    email_confirmed = models.BooleanField(
        default=False,
    )
    birth_year = models.IntegerField(
        default=0,
        blank=True
    )
    height = models.IntegerField(
        default=0,
        help_text='Height in cm',
        blank=True
    )
    gender = models.CharField(
        choices=[('', ' '), ('m', 'Male'), ('f', 'Female')],
        default='',
        max_length=1,
        blank=True
    )
    objects = ProfileManager()

    @property
    def age(self) -> Optional[int]:
        if self.birth_year:
            return datetime.now().year - self.birth_year

    def __str__(self):
        return self.user.username + '_profile'

    def all_datapoints(self):
        return self.user_datapoints.order_by('parameter', '-date').all()

    def summary_data(self):
        return self.user_datapoints.order_by(
            'parameter', '-date').distinct('parameter')

    def get_linked_profile_parameters(self):
        return {a.parameter.name: a.linked_parameter.name
                for a in self.profile_parameters.all() if a.linked_parameter}

    def get_summary_data(self) -> List[dict]:
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

    def get_share_requests(self, request_type='', active=False) -> List[dict]:
        child_fk, name_suffix = 'requester', 'received'
        if request_type == 'made':
            child_fk, name_suffix = 'receiver', 'requested'
        return [a.get_id_and_profile(child_fk) for a in
                getattr(self, f'shares_{name_suffix}').filter(enabled=active)]

    def get_active_shares(self) -> List[dict]:
        active_shares = []
        for s in ['made', '']:
            for dct in self.get_share_requests(s, active=True):
                active_shares.append(
                    {k if k in ['id', 'profile_id'] else 'name': v
                     for k, v in dct.items()}
                )
        return list(sorted(active_shares, key=itemgetter('name')))

    def get_bookmarks_data(self) -> List[dict]:
        return [
            {**{field: getattr(obj, field) for field in
             ['id', 'url', 'title', 'parameter_id']},
             **{'param_id': obj.parameter.id,
                'param_name': obj.parameter.name}}
            for obj in self.user_bookmarks.all()
        ]
