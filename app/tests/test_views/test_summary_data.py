from collections import namedtuple
from unittest.mock import patch

from rest_framework.test import force_authenticate

from app.tests.base import BaseTestCase
from app.tests.mock_objects import LazyAttrObj, MockObj, MockRequest
from app.views.profile.summary_data import ProfileSummaryData


class SummaryDataTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.view = ProfileSummaryData()
        self.request = MockRequest(user=self.profile_1.user)
        force_authenticate(self.request, user=self.profile_1.user)

    def test_dispatch_with_profile_id_kwargs_not_provided(self):
        self.view.dispatch(self.request)
        self.assertIsNone(self.view.shared_profile)

    def test_dispatch_with_profile_id_kwargs_provided(self):
        self.view.dispatch(self.request, profile_id=str(self.profile_1.id))
        self.assertEqual(self.profile_1, self.view.shared_profile)

    def test_get_method_with_view_has_shared_profile_auth_check(self):
        SharedProfile = namedtuple('test_shared_prof', 'get_active_shares')
        self.view.shared_profile = SharedProfile(lambda: [])
        self.assertEqual(401, self.view.get(self.request).status_code)

    @patch('app.views.profile.summary_data.ProfileSummaryData.get_serializers')
    def test_get_method_with_view_has_shared_profile_bad_request(self, gs_pch):
        SharedProfile = namedtuple('test_shared_prof', 'get_active_shares')
        self.view.shared_profile = SharedProfile(
            lambda: [{'profile_id': self.profile_1.id}]
        )
        MockSerializer = namedtuple('mock_ser', ['is_valid', 'errors'])
        gs_pch.return_value = [MockSerializer(lambda: False, 'error_msg')
                               for _ in range(4)]
        self.assertEqual(400, self.view.get(self.request).status_code)

    @patch('app.views.profile.summary_data.ProfileSummaryData.'
           'update_with_ideals_data')
    @patch('app.views.profile.summary_data.ProfileSummaryData.'
           'update_with_units_options')
    @patch('app.views.profile.summary_data.ProfileSummaryData.'
           'update_with_stats_data')
    @patch('app.views.profile.summary_data.ProfileParamUnitOption.'
           'param_unit_opt_dct')
    @patch('app.views.profile.summary_data.ProfileSummaryData.get_serializers')
    def test_get_method_success_response(self, gs_pch, ppuo_pch, p1, p2, p3):
        for s in ['get_share_requests', 'get_linked_profile_parameters']:
            setattr(self.profile_1, s, lambda: '')
        MockSerializer = namedtuple('mock_ser', ['is_valid', 'data'])
        gs_pch.return_value = [MockSerializer(lambda: 1, '')
                               for _ in range(4)]
        resp = self.view.get(self.request)
        self.assertEqual(200, resp.status_code)
        for k in ['share_requests_received', 'date_formats',
                  'share_requests_received', 'linked_parameters',
                  'linked_parameters', 'blank_params']:
            self.assertTrue(k in resp.data)
        self.assertEqual(self.view.shared_profile is not None,
                         resp.data['is_shared_view'])

    @patch('app.views.profile.summary_data.BookmarkSerializer')
    @patch('app.views.profile.summary_data.DataPointSerializer')
    @patch('app.views.profile.summary_data.ParameterSerializer')
    @patch('app.views.profile.summary_data.SummaryDataSerializer')
    def test_get_serializers(self, p1, p2, p3, p4):
        mock_param = MockObj(num_values=34, name='test_name')
        nt_fields = ['parameter', 'id', 'date', 'value', 'value2', 'qualifier']
        TestObj = namedtuple('param_nt', nt_fields)

        def mock_all_datapoints():
            return [TestObj(mock_param, *['' for _ in nt_fields[1:]])]
        self.profile_1.all_datapoints = mock_all_datapoints
        for s in ['get_bookmarks_data', 'get_summary_data']:
            setattr(self.profile_1, s, lambda: '')
        self.assertEqual(4, len(self.view.get_serializers(self.profile_1)))
        for pch in [p1, p4]:
            self.assertEqual({'data': '', 'many': True},
                             getattr(pch, 'call_args')[1])

    @patch('app.views.profile.summary_data.CalcParamIdeal')
    def test_update_with_ideals_data(self, cpi_pch):
        cpi_pch.return_value = MockObj(
            get_ideal_data=lambda: {k: f'{k}_val' for k in ['ideal', 'ideal2']},
            required_field=True, misc_data={'a': 'b', 'param_name': 'p_name'}
        )
        initial = {'blank_params': [{'name': 'no_unit_opt_exists_for_name'}],
                   'profile_summary': []}
        self.view.update_with_ideals_data(initial, self.profile_2)
        self.assertEqual(
            [{'saved': None, 'saved2': None, 'missing_field': True,
              'misc_info': {'a': 'b', 'param_name': 'p_name'},
              'param_name': 'no_unit_opt_exists_for_name',
              'ideal': 'ideal_val', 'ideal2': 'ideal2_val',
              'ideal_prepend': '', 'ideal2_prepend': ''}],
            initial['ideals'])
        self.assertEqual(
            [namedtuple('ppo', ['param_name', 'pp_unit_option'])(
                initial['blank_params'][0]['name'], None)],
            self.view.profile_params
        )

    @patch('app.models.profile_parameter.ProfileParamUnitOption.'
           'get_unit_info')
    def test_update_with_units_options(self, gui_pch):
        gui_pch.return_value = 'gui_mock'
        self.view.profile_params = [LazyAttrObj()]
        initial = {}
        self.view.update_with_units_options(initial)
        self.assertEqual({'unit_info': ['gui_mock']}, initial)

    @patch('app.views.profile.summary_data.get_rolling_mean')
    @patch('app.views.profile.summary_data.get_monthly_means')
    def test_update_with_stats_data(self, gmm_pch, grm_pch):
        initial = {'datapoints': [{'parameter': 'p1', 'val': 1},
                                  {'parameter': 'p2', 'val': 2}]}
        ProfileSummaryData.update_with_stats_data(initial)
        self.assertEqual(initial['rolling_means'],
                         [grm_pch.return_value for _ in initial['datapoints']])
        self.assertEqual(initial['monthly_changes'],
                         [gmm_pch.return_value for _ in initial['datapoints']])
