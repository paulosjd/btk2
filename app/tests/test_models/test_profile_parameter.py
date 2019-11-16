from collections import namedtuple
from unittest.mock import patch

from app.models import ProfileParamUnitOption
from app.tests.base import BaseTestCase

mock_ideals_data = {k: f'{k}_val' for k in
                    ['ideal2_prepend', 'ideal', 'ideal2', 'ideal_prepend']}


class MockCalcParamIdeal:
    def __init__(self, *args):
        self.required_field = 'abc'
        self.misc_data = 'def'
        self.get_ideal_data = lambda: mock_ideals_data
        self.get = lambda key, default: mock_ideals_data.get(key, default)


class ProfileParameterTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(ProfileParameterTestCase, cls).setUpClass()
        cls.profile_param_unit_opt = cls.profile_1.profile_parameters.first()
        cls.profile_param_unit_opt.target_value = 34.5
        cls.profile_param_unit_opt.linked_parameter = cls.param2
        cls.profile_param_unit_opt.save()

    @patch('app.models.profile_parameter.CalcParamIdeal')
    def test_targets_method(self, cpi_patch):
        nt_fields = ['saved', 'saved2', 'misc_data', 'required_field', 'ideal',
                     'ideal2', 'ideal_prepend', 'ideal2_prepend']
        cpi_patch.return_value = MockCalcParamIdeal()
        ExpectedTargetData = namedtuple('target_data', nt_fields)
        expected_nt_returned = ExpectedTargetData(
            self.profile_param_unit_opt.target_value,
            self.profile_param_unit_opt.target_value2,
            cpi_patch.return_value.misc_data,
            cpi_patch.return_value.required_field,
            *[mock_ideals_data.get(k, '') for k in nt_fields[-4:]]
        )
        self.assertEqual(expected_nt_returned,
                         self.profile_param_unit_opt.targets('lat_val_1'))

    def test_get_unit_info_falsey(self):
        TestObj = namedtuple('test_obj', 'pp_unit_option')
        test_obj = TestObj(None)
        self.assertIsNone(ProfileParamUnitOption.get_unit_info(test_obj))

    def test_get_unit_info(self):
        TestObj = namedtuple('test_obj', ['pp_unit_option', 'param_name'])
        model = self.profile_param_unit_opt
        model.color_hex = 'blue'
        for a, b in [(5, '1'), (6, '2')]:
            setattr(model, f'color_range_val_{b}', a)
        test_obj = TestObj(model, 'p_name')
        expected_output = {
            k: getattr(test_obj.pp_unit_option.unit_option, k)
            for k in ['param_default', 'conversion_factor', 'symbol']
        }
        expected_output.update({'color_hex': 'blue', 'color_range_val_1': 5,
                                'color_range_val_2': 6, 'param_name': 'p_name'})
        self.assertEqual(expected_output,
                         ProfileParamUnitOption.get_unit_info(test_obj))

    def test_param_unit_opt_dct(self):
        fields = ['symbol', 'name', 'param_default', 'conversion_factor']
        TestObj = namedtuple('test_obj', fields)
        test_obj = TestObj(*[f'{s}_val' for s in fields])
        self.assertEqual(
            {f'unit_{s}': getattr(test_obj, s) for s in fields},
            ProfileParamUnitOption.param_unit_opt_dct(test_obj)
        )
