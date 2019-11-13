from django.core.exceptions import ValidationError

from app.models import Parameter
from app.tests.base import BaseTestCase


class ParameterTestCase(BaseTestCase):

    def test_available_unit_options(self):
        self.assertEqual(
            [{s: getattr(unit_choice, s) for s in
              ['name', 'symbol', 'conversion_factor']}
             for unit_choice in self.param1.unit_choices.all()],
            self.param1.available_unit_options
        )

    def test_save_validation_error_if_upload_fields_mismatch(self):
        self.param1.upload_field_labels = 'a, b, c'
        with self.assertRaises(ValidationError):
            self.param1.save()

    def test_save_validation_error_if_upload_fields_mismatch_2(self):
        self.param1.num_values = 5
        with self.assertRaises(ValidationError):
            self.param1.save()

    def test_available_parameters_for_profile(self):
        self.assertEqual(
            list(Parameter.objects.union(
                Parameter.objects.custom_parameters().filter(
                    profile=self.profile_1)
            ).all()),
            list(Parameter.available_parameters_for_profile(self.profile_1)),
        )

    def test_create_custom_metric_already_exists(self):
        self.assertEqual(
            (False, 'Name already exists'),
            Parameter.create_custom_metric(self.profile_1, self.param2.name, '')
        )

    def test_create_custom_metric_with_unique_constraint_broken(self):
        self.assertEqual(
            (False, 'Invalid data'),
            Parameter.create_custom_metric(self.profile_1, 'abc', None)
        )

    def test_create_custom_metric(self):
        self.assertIsInstance(
            Parameter.create_custom_metric(self.profile_1, 'foo', 'bar')[0],
            Parameter
        )
