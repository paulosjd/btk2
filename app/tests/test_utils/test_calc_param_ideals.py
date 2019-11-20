from unittest import TestCase

from app.tests.mock_objects import MockObj
from app.utils import CalcParamIdeal


class CalcParamIdealsTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.mock_profile = MockObj(age=32, gender='m', height=174)
        self.init_args = ['', self.mock_profile]
        self.init_kwargs = {'latest_val': 56.2, 'latest_val2': 48.2,
                            'unit_symbol': 'kg'}
        self.instance = CalcParamIdeal(*self.init_args, **self.init_kwargs)

    def test_get_ideal_data_with_no_calc_method_defined(self):
        self.instance.calc_method = ''
        self.assertEqual({}, self.instance.get_ideal_data())

    def test_get_ideal_data_calls_correct_method(self):
        self.instance.calc_method = lambda: 23
        self.assertEqual(23, self.instance.get_ideal_data())

    def test_body_weight_calc_method_profile_not_has_height(self):
        self.mock_profile.height = 0
        self.assertIsNone(self.instance.body_weight())
        self.assertEqual('Height', self.instance.required_field)

    def test_body_weight_calc_method_profile_has_height(self):
        ht = self.instance.profile.height / 100
        bmi = round((self.instance.latest_val / self.instance.conversion_factor
                     ) / ht ** 2, 1)
        self.assertEqual(
            {'ideal': round(2.2 * bmi + 3.5 * bmi * (ht - 1.5), 1)},
            self.instance.body_weight()
        )
        self.assertEqual(
            [f'Body mass index (BMI): {bmi} kg/m\N{SUPERSCRIPT TWO}'],
            self.instance.misc_data
        )

    def test_resting_heart_rate_method_with_not_profile_age(self):
        self.instance.profile.age = None
        self.assertIsNone(self.instance.resting_heart_rate())
        self.assertEqual(self.instance.required_field, 'Age')

    def test_resting_heart_rate_method_with_profile_has_age(self):
        self.instance.profile.age = 46
        self.assertEqual(
            {'ideal': int(60 + (self.instance.profile.age - 20)/2)},
            self.instance.resting_heart_rate()
        )

    def test_resting_heart_rate_method_with_profile_has_age_2(self):
        self.instance.profile.age = 16
        self.assertEqual({'ideal': 60}, self.instance.resting_heart_rate())

    def test_blood_pressure_method_with_not_profile_age(self):
        self.instance.profile.age = None
        self.assertIsNone(self.instance.blood_pressure())
        self.assertEqual(self.instance.required_field, 'Age')

    def test_blood_pressure_method_profile_has_age(self):
        self.assertEqual({'ideal': 120, 'ideal2': 80,
                          'ideal2_prepend': '<', 'ideal_prepend': '<'},
                         self.instance.blood_pressure())

    def test_blood_chol_calc_method_handles_typeerror(self):
        self.instance.latest_val2 = 'abc'
        self.instance.profile.gender = 'f'
        self.assertEqual({'ideal': 1.6, 'ideal2': 2.6, 'ideal_prepend': '>',
                          'ideal2_prepend': '<'},
                         self.instance.blood_cholesterol())
        self.assertEqual(['Recommended LDL/HDL ratio: 3.0'],
                         self.instance.misc_data)

    def test_blood_chol_calc_method(self):
        self.assertEqual({'ideal': 1.6, 'ideal2': 2.6, 'ideal_prepend': '>',
                          'ideal2_prepend': '<'},
                         self.instance.blood_cholesterol())
        ratio = round(self.instance.latest_val2/self.instance.latest_val, 1)
        self.assertEqual(['Recommended LDL/HDL ratio: 3.5',
                          f'LDL/HDL ratio: {ratio}'],
                         self.instance.misc_data)

    def test_fasting_blood_glucose(self):
        self.assertEqual({'ideal_prepend': '<',
                          'ideal': 4.2 * self.instance.conversion_factor},
                         self.instance.fasting_blood_glucose())
