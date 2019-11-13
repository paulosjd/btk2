from collections import namedtuple
from datetime import datetime, date
from unittest.mock import patch

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from app.models import DataPoint
from app.tests.base import BaseTestCase


class DataPointTestCase(BaseTestCase):
    ResultNT = namedtuple('BulkCreateResult', ['success', 'message'])

    @classmethod
    def setUpClass(cls):
        super(DataPointTestCase, cls).setUpClass()
        cls.profile_param_unit_opt = cls.profile_1.profile_parameters.first()
        cls.profile_param_unit_opt.target_value = 34.5
        cls.profile_param_unit_opt.linked_parameter = cls.param2
        cls.profile_param_unit_opt.save()
        cls.dp_data = dict(profile=cls.profile_1, parameter=cls.param1,
                           date=datetime.today(), value=20)
        cls.data_point = DataPoint.objects.create(**cls.dp_data)

    @patch('app.models.data_point.ProfileParamUnitOption.get_unit_option',
           side_effect=ObjectDoesNotExist)
    def test_save_with_profile_and_param_none_raises(self, guo_pch):
        dp = DataPoint(value=2, date=datetime.now().date(),
                       profile=self.profile_1, parameter=self.param2)
        with self.assertRaises(ValidationError):
            dp.save()

    def test_bulk_create_from_csv_upload_already_exists(self):
        self.assertEqual(
            self.ResultNT(False, f"{self.dp_data['parameter'].name} data on "
                                 f"{self.dp_data['date']} already exists"),
            DataPoint.bulk_create_from_csv_upload([self.dp_data])
        )

    def test_bulk_create_from_csv_upload_handles_value_error(self):
        dp_dct_cp = self.dp_data.copy()
        dp_dct_cp['parameter'] = None
        self.assertEqual(self.ResultNT(False, ''),
                         DataPoint.bulk_create_from_csv_upload([dp_dct_cp]))

    def test_bulk_create_from_csv_upload(self):
        dp_dct_cp = self.dp_data.copy()
        dp_dct_cp['parameter'] = self.param2
        self.assertEqual(self.ResultNT(True, ''),
                         DataPoint.bulk_create_from_csv_upload([dp_dct_cp]))

    def test_update_on_date_match_or_create_returns_none_if_key_error(self):
        self.assertIsNone(DataPoint.update_on_date_match_or_create(k=2))

    @patch('app.models.data_point.ProfileParamUnitOption.get_unit_option')
    def test_update_on_date_match_or_create_creates_on_no_date_match(self, pch):
        kwargs = self.dp_data.copy()
        kwargs.update({'profile': self.profile_2, 'date': date(2012, 3, 5)})
        count1 = DataPoint.objects.count()
        DataPoint.update_on_date_match_or_create(**kwargs)
        self.assertEqual(1, DataPoint.objects.count() - count1)

    @patch('app.models.data_point.ProfileParamUnitOption.get_unit_option')
    def test_update_on_date_match_or_create_updates_on_date_match(self, pch):
        kwargs = {k: getattr(self.data_point, k) for k in
                  ['parameter', 'profile', 'date']}
        kwargs['value'] = 45.2
        count1 = DataPoint.objects.count()
        DataPoint.update_on_date_match_or_create(**kwargs)
        self.assertEqual(count1, DataPoint.objects.count())
        self.assertEqual(
            kwargs['value'],
            DataPoint.objects.get(parameter=self.data_point.parameter,
                                  profile=self.data_point.profile,
                                  date=self.data_point.date).value
        )

