from collections import namedtuple
from datetime import datetime
from operator import itemgetter
from unittest.mock import patch

from app.models import Bookmark, ProfileShare
from app.tests.base import BaseTestCase

ppuo_path = 'app.models.profile_parameter.ProfileParamUnitOption'
view_path = 'app.models.profile_share.ProfileShare'


class ProfileTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(ProfileTestCase, cls).setUpClass()
        cls.profile_1.email_confirmed = True
        cls.profile_2.email_confirmed = True
        cls.share1 = ProfileShare.objects.create(
            requester=cls.profile_1, receiver=cls.profile_2, enabled=False,
        )
        cls.share2 = ProfileShare.objects.create(
            requester=cls.profile_1, receiver=cls.profile_2, enabled=True
        )
        cls.share3 = ProfileShare.objects.create(
            requester=cls.profile_2, receiver=cls.profile_1, enabled=True
        )
        cls.share4 = ProfileShare.objects.create(
            requester=cls.profile_2, receiver=cls.profile_1, enabled=False
        )
        cls.bookmark = Bookmark.objects.create(
            url='test_url_1', profile=cls.profile_1, parameter=cls.param1
        )

    def test_age_property_returns_none_if_not_birth_year(self):
        self.assertIsNone(self.profile_1.age)

    def test_age_property_returns_correct_int_if_birth_year(self):
        self.assertEqual(datetime.now().year - self.profile_2.birth_year,
                         self.profile_2.age)

    def test_get_linked_profile_parameters(self):
        expected_qs = [self.profile_param_unit_opt]
        self.assertEqual(
            {a.parameter.name: a.linked_parameter.name for a in expected_qs},
            self.profile_1.get_linked_profile_parameters()
        )

    @patch(f'{ppuo_path}.param_unit_opt_dct', return_value={})
    @patch(f'{ppuo_path}.get_unit_option')
    @patch('app.models.profile.Profile.summary_data')
    def test_get_summary_data(self, sum_data_patch, guo_pch, puod_pch):
        param_fields = [
            'name', 'upload_fields', 'upload_field_labels', 'ideal_info',
            'ideal_info_url', 'id', 'num_values'] + [f'value2_short_label_{i}'
                                                     for i in [1, 2]]
        ParamObj = namedtuple('param', param_fields)
        pos = [ParamObj(*[f'{i}_{pf}' for pf in param_fields]) for i in [1, 2]]
        SdObj = namedtuple('sd_obj', ['parameter', 'date', 'value', 'value2'])
        sum_data_obj_list = [SdObj(pos[0], 'a', 'b', 'c'),
                             SdObj(pos[1], 'd', 'e', 'f')]
        sum_data_patch.return_value = sum_data_obj_list
        expected_return_val = [{
            'parameter': {field: getattr(obj.parameter, field)
                          for field in param_fields},
            'data_point': {field: getattr(obj, field)
                           for field in ['date', 'value', 'value2']},
        } for i, obj in enumerate(sum_data_obj_list)]
        self.assertEqual(expected_return_val, self.profile_1.get_summary_data())

    @patch(f'{view_path}.get_id_and_profile', return_value={'a': '2'})
    def test_get_share_requests_with_default_params(self, get_id_and_profile_p):
        child_fk, name_suffix = 'requester', 'received'
        self.assertEqual(
            [{**get_id_and_profile_p.return_value, 'message': a.message}
             for a in getattr(self.profile_1,
                              f'shares_{name_suffix}').filter(enabled=False)],
            self.profile_1.get_share_requests()
        )

    @patch(f'{view_path}.get_id_and_profile', return_value={'b': '5'})
    def test_get_share_requests_non_default_params(self, get_id_and_profile_p):
        child_fk, name_suffix = 'receiver', 'requested'
        self.assertEqual(
            [{**get_id_and_profile_p.return_value, 'message': a.message}
             for a in getattr(self.profile_1,
                              f'shares_{name_suffix}').filter(enabled=False)],
            self.profile_1.get_share_requests('made')
        )

    @patch('app.models.profile.Profile.get_share_requests')
    def test_get_active_shares(self, get_share_reqs_patch):
        mock_return_val = [
            {k: f'{k}_val1' for k in ['id', 'profile_id', 'foo']},
            {k: f'{k}_val2' for k in ['id', 'profile_id', 'bar']},
        ]

        def mock_get_share_reqs(s, active):
            return [mock_return_val[0 if s == 'made' else 1]]

        get_share_reqs_patch.side_effect = mock_get_share_reqs
        self.assertEqual(
            list(sorted(
                [{**{k: f'{k}_val1' for k in ['id', 'profile_id']},
                  **{'name': 'foo_val1'}},
                 {**{k: f'{k}_val2' for k in ['id', 'profile_id']},
                  **{'name': 'bar_val2'}}],
                key=itemgetter('name'))),
            self.profile_1.get_active_shares()
        )

    def test_get_bookmarks_data(self):
        self.assertEqual(
            [{**{field: getattr(obj, field) for field in
                 ['id', 'url', 'title', 'parameter_id']},
              **{'param_id': obj.parameter.id, 'param_name': obj.parameter.name}
              } for obj in self.profile_1.user_bookmarks.all()],
            self.profile_1.get_bookmarks_data()
        )
