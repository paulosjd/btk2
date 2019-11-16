from datetime import datetime
from unittest.mock import patch

from rest_framework.test import force_authenticate

from app.models import Parameter
from app.tests.base import BaseTestCase
from app.tests.mock_objects import MockObj, MockRequest
from app.views.data_point.add_data_points import AddDataPoints

file_path = 'app.views.data_point.add_data_points'


class AddDataPointsTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.view = AddDataPoints()
        self.view.json_response = lambda: 'some_json'
        self.request = MockRequest(method='POST', user=self.profile_1.user)
        force_authenticate(self.request, user=self.profile_1.user)

    @patch(f'{file_path}.AddDataPoints.process_post_data')
    def test_post_1(self, ppd_pch):
        self.request.data = {
            'value': {'parameter': 'should_not_get_result'}
        }
        self.assertEqual('some_json', self.view.post(self.request))
        self.assertEqual(0, ppd_pch.call_count)

    @patch(f'{file_path}.AddDataPoints.process_post_data')
    def test_post_2(self, ppd_pch):
        self.request.data = {
            'value': {'parameter': Parameter.objects.first().name, 'foo': 'bar'}
        }
        self.assertEqual('some_json', self.view.post(self.request))
        self.assertEqual(1, ppd_pch.call_count)
        self.assertEqual(
            (self.request.data['value'], Parameter.objects.first()),
            ppd_pch.call_args[0]
        )

    @patch(f'{file_path}.DataPoint.update_on_date_match_or_create')
    def test_process_post_data_with_catch_key_error(self, uodmoc_pch):
        mock_param = MockObj(upload_fields='value')
        bad_input = {'0_date': '2018-10-10', '0_xyz': '',
                     '1_date': '2018-10-12', '1_khl': '64'}
        self.view.process_post_data(bad_input, mock_param)
        self.assertEqual(0, uodmoc_pch.call_count)

    @patch(f'{file_path}.DataPoint.update_on_date_match_or_create')
    def test_process_post_data_handles_value_error(self, uodmoc_pch):
        mock_param = MockObj(upload_fields='value')
        bad_input = {'0_date': '2018-10-10', '0_value': '',
                     '1_date': 'bad date format', '1_value': 'NaN',
                     '2_date': '2018-10-12', '2_value': '64'}
        self.view.request = self.request
        self.view.process_post_data(bad_input, mock_param)
        self.assertEqual(1, uodmoc_pch.call_count)
        self.assertEqual(
            {'parameter': mock_param, 'profile': self.request.user.profile,
             'value': round(float(bad_input['2_value']), 2),
             'date': datetime.strptime(bad_input['2_date'], '%Y-%m-%d')},
            uodmoc_pch.call_args[1]
        )

    @patch(f'{file_path}.DataPoint.update_on_date_match_or_create')
    def test_process_post_data_with_valid_input_data(self, uodmoc_pch):
        mock_param = MockObj(upload_fields='value')
        bad_input = {'0_date': '2018-10-10', '0_value': '58.6',
                     '1_date': '2018-10-12', '1_value': '64'}
        self.view.request = self.request
        self.view.process_post_data(bad_input, mock_param)
        self.assertEqual(2, uodmoc_pch.call_count)
