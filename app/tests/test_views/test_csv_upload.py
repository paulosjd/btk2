from unittest.mock import Mock, patch

from rest_framework.test import force_authenticate

from app.models import Parameter, UnitOption, ProfileParamUnitOption
from app.serializers import DataPointSerializer
from app.tests.base import BaseTestCase
from app.tests.mock_objects import MockObj, MockRequest
from app.views.data_point.csv_upload import CsvUploadView

file_path = 'app.views.data_point.csv_upload'


class MockCsvProcessor:
    def __init__(self, fields, data, **kwargs):
        super().__init__(**kwargs)
        self.is_valid = True
        self.fields = fields
        self.data = data

    def __iter__(self):
        return iter(self.data)


class CsvUploadViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.view = CsvUploadView()
        self.request = MockRequest(method='POST', user=self.profile_1.user)
        force_authenticate(self.request, user=self.profile_1.user)
        self.csv_test_param = Parameter.objects.create(
            name='Csv Upload Test', profile=self.profile_1, is_builtin=True,
            **self.param_extras
        )
        self.prof2_csv_param_unit_opt = self.profile_1.profile_parameters.get(
            parameter=self.csv_test_param
        )
        self.unit_opt = UnitOption.objects.create(
            name='Test metric A', symbol='$', is_builtin=True,
            parameter=self.csv_test_param
        )

    def test_post_method_missing_data(self):
        self.request.data = {'date_fmt': 'some bad format', 'file': None}
        self.assertEqual(400, self.view.post(self.request).status_code)

    def test_post_method_with_file_in_data_but_param_name_query_falsey(self):
        self.request.data = {'date_format': 'YYYY/MM/DD', 'file': 'myfile',
                             'param_choice': 'dfg3r43$23sf!23'}
        self.assertEqual(400, self.view.post(self.request).status_code)

    @patch(f'{file_path}.CsvToModelData')
    def test_post_with_file_in_request_data_not_is_valid(self, csv2md_pch):
        req_params = {'param_choice': self.csv_test_param.name, 'file': 'file5',
                      'unit_choice': 'test_uc', 'date_format': 'YYYY/MM/DD'}
        self.request.data = req_params
        expected_meta_dict = {
            'field_order': self.csv_test_param.upload_fields.split(', '),
            'param_id': self.csv_test_param.id,
            'date_fmt': self.date_fmt_opts_map[req_params['date_format']],
            'unit_choice': req_params['unit_choice']
        }
        csv2md_pch.return_value = MockObj(is_valid=False, error='abc')

        resp = self.view.post(self.request)
        self.assertEqual(400, resp.status_code)
        self.assertEqual({'error': 'abc'}, resp.data)
        self.assertEqual((req_params['file'], expected_meta_dict),
                         csv2md_pch.call_args[0])

    @patch(f'{file_path}.CsvToModelData', autospec=True)
    def test_post_with_file_in_request_data_is_valid(self, csv2md_pch):
        req_params = {'param_choice': self.csv_test_param.name, 'file': 'file5',
                      'unit_choice': 'test_uc', 'date_format': 'YYYY/MM/DD'}
        self.request.data = req_params
        dp_fields = self.csv_test_param.upload_fields.split(', ')
        csv2md = MockCsvProcessor(dp_fields,
                                  [MockObj(**{dp_fields[0]: a, dp_fields[1]: b})
                                   for a, b in [('a', 2), ('b', 3)]])
        csv2md_pch.return_value = csv2md
        expected_resp_data = {
            'data': [{k: getattr(obj, k) for k in dp_fields}
                     for obj in csv2md],
            'meta': {
                'field_order': dp_fields,
                'param_id': self.csv_test_param.id,
                'date_fmt': self.date_fmt_opts_map[req_params['date_format']],
                'unit_choice': req_params['unit_choice']
            }
        }

        resp = self.view.post(self.request)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(expected_resp_data, resp.data)

    def test_post_serializer_is_valid_unit_opt_not_found(self):
        data = [{'a': i, 'b': i + 1} for i in [0, 2]]
        meta = {'param_id': self.csv_test_param.id, 'unit_choice': '4er%E$sfe'}
        self.request.data = {'data': {
            'data': data, 'meta': meta, 'confirm': True
        }}
        expected_data_list = [{**dct, **{'parameter': self.csv_test_param.id,
                                         'profile': self.profile_1.id}}
                              for dct in data]

        self.view.serializer_class = Mock()
        resp = self.view.post(self.request)
        self.assertEqual({'data': expected_data_list, 'many': True},
                         self.view.serializer_class.call_args[1])
        self.assertEqual({'error': self.view.error_msg}, resp.data)

    @patch.object(DataPointSerializer, 'is_valid', return_value=False)
    def test_post_with_serializer_is_not_valid(self, dp_ser_pch):
        self.request.data = {'data': {
            'data': [{'a': 2}], 'confirm': True,
            'meta': {'param_id': self.csv_test_param.id, 'unit_choice': 'a'},
        }}
        dp_ser_pch.return_value = self.view.serializer_class
        resp = self.view.post(self.request)
        self.assertEqual(400, resp.status_code)
        self.assertEqual({'error': self.view.error_msg}, resp.data)

    @patch(f'{file_path}.DataPoint.bulk_create_from_csv_upload')
    def test_post_valid_bulk_create_fail(self, bcfcu_pch):
        bcfcu_pch.return_value = MockObj(message='test msg', success=False)
        meta = {'param_id': self.csv_test_param.id,
                'unit_choice': self.unit_opt.name}
        self.request.data = {'data': {'data': [{'a': 2}],
                                      'meta': meta,
                                      'confirm': True}}
        self.view.serializer_class = Mock(return_value=MockObj(
            is_valid=lambda: True, data=[{}]
        ))

        resp = self.view.post(self.request)
        self.assertEqual([{'parameter': self.csv_test_param,
                           'profile': self.request.user.profile}],
                         bcfcu_pch.call_args[0][0]),
        self.assertEqual({'error': bcfcu_pch.return_value.message}, resp.data)

    @patch.object(ProfileParamUnitOption.objects, 'get_or_create')
    @patch(f'{file_path}.DataPoint.bulk_create_from_csv_upload')
    def test_post_valid_bulk_create_success(self, bcfcu_pch, goc_pch):
        bcfcu_pch.return_value = MockObj(message='', success=True)
        meta = {'param_id': self.csv_test_param.id,
                'unit_choice': self.unit_opt.name}
        self.request.data = {'data': {'data': [{'a': 2}],
                                      'meta': meta,
                                      'confirm': True}}
        self.view.serializer_class = Mock(return_value=MockObj(
            is_valid=lambda: True, data=[{}]
        ))

        resp = self.view.post(self.request)
        self.assertEqual([{'parameter': self.csv_test_param,
                           'profile': self.request.user.profile}],
                         bcfcu_pch.call_args[0][0]),
        self.assertEqual(200, resp.status_code)
