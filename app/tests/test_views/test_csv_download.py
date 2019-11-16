import csv
from datetime import datetime
from unittest.mock import patch

from django.http import HttpResponse
from rest_framework.test import force_authenticate

from app.models import DataPoint, Parameter
from app.tests.base import BaseTestCase
from app.tests.mock_objects import MockObj, MockRequest
from app.views.data_point.csv_download import CsvDownloadView


class CsvDownloadViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.view = CsvDownloadView()
        self.request = MockRequest(method='POST', user=self.profile_1.user)
        force_authenticate(self.request, user=self.profile_1.user)
        self.param3 = Parameter.objects.create(
            name='p3name', profile=self.profile_2, is_builtin=True,
            **self.param_extras
        )
        self.param4 = Parameter.objects.create(
            name='p4name', profile=self.profile_2, is_builtin=True,
            **self.param_extras,
        )
        self.dp_data = dict(profile=self.profile_1, parameter=self.param1,
                            date=datetime.today(), value=20)
        self.dp_data2 = dict(profile=self.profile_1, parameter=self.param1,
                             date=datetime(2018, 10, 12).date(), value=5)
        self.data_point = DataPoint.objects.create(**self.dp_data)
        self.data_point2 = DataPoint.objects.create(**self.dp_data2)

    def test_post_method_missing_data(self):
        self.request.data = {'date_fmt': 'some bad format', 'fields': []}
        self.assertEqual(400, self.view.post(self.request).status_code)

    @patch('app.views.data_point.csv_download.CsvDownloadView.get_rows')
    @patch('app.views.data_point.csv_download.CsvDownloadView.'
           'get_headers_labels')
    @patch('app.views.data_point.csv_download.CsvDownloadView.init')
    def test_post_method_valid_input_data(self, init_pch, ghl_pch, gr_pch):
        header_labels = ['a', 'b']
        rows = [['32', '34'], ['42', '35']]
        ghl_pch.return_value = header_labels
        gr_pch.return_value = rows
        date_fmt = 'YYYY/MM/DD'
        fields = [a.name for a in [self.param3, self.param4]]
        self.request.data = {'date_fmt': date_fmt, 'fields': fields}
        self.request.user.profile = self.profile_2
        expected_response = HttpResponse(content_type='text/csv')
        expected_response['Content-Disposition'] = \
            f'attachment; filename="{self.profile_2.user.username}_data.csv"'
        writer = csv.writer(expected_response)
        writer.writerow(header_labels)
        for row in rows:
            writer.writerow(row)
        self.assertEqual(expected_response.serialize(),
                         self.view.post(self.request).serialize())
        self.assertEqual(([self.param3, self.param4],
                          self.date_fmt_opts_map.get('YYYY/MM/DD')),
                         init_pch.call_args[0])

    def test_init_method(self):
        parameters = [a.parameter for a in [self.data_point, self.data_point2]]
        dt_fmt = '%Y/%m/%d '
        self.view.param_cols = {}
        self.view.parameters = []
        expected_set_param_cols = {}
        expected_set_params = []
        self.request.user.profile = self.data_point.profile
        for param in parameters:
            param_dpts = DataPoint.objects.filter(
                profile=self.request.user.profile, parameter=param
            ).all()
            param_sub_rows = [
                [getattr(a, field) for field in param.upload_fields.split(', ')]
                for a in param_dpts
            ]
            for ind, ps in enumerate(param_sub_rows):
                param_sub_rows[ind][0] = param_sub_rows[ind][0].strftime(dt_fmt)
            expected_set_param_cols[param.name] = param_sub_rows
            expected_set_params.append(param)
        expected_set_params = list(reversed(
            sorted(expected_set_params,
                   key=lambda x: len(expected_set_param_cols))
        ))
        self.view.request = self.request
        self.view.init(parameters, dt_fmt)
        self.assertEqual(expected_set_param_cols, self.view.param_cols)
        self.assertEqual(expected_set_params, self.view.parameters)

    @patch('app.views.data_point.csv_download.ProfileParamUnitOption.'
           'get_unit_option')
    def test_get_headers_labels(self, guo_pch):
        symbol = 'mg/L'
        guo_pch.return_value = MockObj(symbol=symbol)
        self.view.parameters = [MockObj(upload_field_labels='Date, Col B'),
                                MockObj(upload_field_labels='Date, Col D')]
        self.view.request = self.request
        self.assertEqual(
            ['Date', f'Col B ({symbol})', '', 'Date', f'Col D ({symbol})'],
            self.view.get_headers_labels()
        )

    def test_get_rows(self):
        param_cols = {'Param name': [
            ['2015/10/11', 75.0], ['2015/10/19', 56.0], ['2018/10/12', 65.0]]}
        self.view.param_cols = param_cols
        self.view.parameters = [MockObj(name='Param name', num_values=1)]
        self.view.request = self.request
        expected_output = []
        for row_num in range(len(param_cols['Param name'])):
            expected_output.append(param_cols['Param name'][row_num])
        self.assertEqual(expected_output, self.view.get_rows())
