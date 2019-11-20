import csv
import io
from unittest import TestCase
from unittest.mock import patch

from app.utils.csv_to_model_data import CsvToModelData

path = 'app.utils.csv_to_model_data.CsvToModelData'


class CsvToModelDataTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.meta_dict = {'field_order': ['date', 'value'],
                          'param_id': 5,
                          'date_fmt': '%d/%m/%y',
                          'unit_choice': 'undefined',
                          'first_row': 1}

    def test_process_csv_handles_attribute_error(self):
        instance = CsvToModelData('no read attribute', self.meta_dict)
        self.assertFalse(instance.process_csv())
        self.assertEqual('Please check formatting and try again',
                         instance.error)

    @patch(f'{path}.shape_isvalid', return_value=True)
    @patch(f'{path}.data_isvalid', return_value=True)
    def test_process_csv(self, disv_p, sisv_p):
        instance = CsvToModelData(io.BytesIO(b'some_data'), self.meta_dict)
        expected_data = list(csv.reader(
            io.BytesIO(b'some_data').read().decode('ISO-8859-1').splitlines()
        ))
        instance.process_csv()
        self.assertEqual(expected_data, instance._model_data)

    @patch(f'{path}.process_csv')
    def test_is_valid_property_1(self, pc_pch):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertFalse(instance.is_valid)

    def test_is_valid_property_2(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        instance._model_data = True
        instance.error = False
        self.assertTrue(instance.is_valid)

    def test_shape_isvalid_bad_input_1(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertFalse(instance.shape_isvalid([['a', 'b', 'c', 'd']]))
        self.assertEqual('Please check formatting and try again',
                         instance.error)

    def test_shape_isvalid_bad_input_2(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertFalse(instance.shape_isvalid([['a', 'b'], ['2', '4', '3']]))
        self.assertEqual('Please check formatting and try again',
                         instance.error)

    def test_shape_isvalid_bad_input_3(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertFalse(instance.shape_isvalid([
            ['Date', 'Value'], ['23', '24'], ['34', ''], ['24', '28']]))
        self.assertEqual('Uploaded file contains missing data',
                         instance.error)

    def test_shape_isvalid(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertTrue(instance.shape_isvalid([
            ['Date', 'Value'], ['23', '24'], ['34', '30'], ['24', '28']]))

    def test_data_isvalid_bad_data_1(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertIsNone(instance.data_isvalid([['a', '2']]))
        self.assertEqual('Column 1: date format issue', instance.error)

    def test_data_isvalid_bad_data_2(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertIsNone(instance.data_isvalid(
            [['10/10/10', '12.4'], ['10/10/10', '13.2'], ['10/10/10', 'a']]))
        self.assertEqual('Format issue: Column 2 Row 3', instance.error)

    def test_data_isvalid_bad_data_3(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        instance.field_types_map = {'date': dict, 'value': float}
        self.assertIsNone(instance.data_isvalid([['10/10/10', '56']]))
        self.assertEqual('Unrecognized field type', instance.error)

    def test_data_isvalid(self):
        instance = CsvToModelData(io.BytesIO(b''), self.meta_dict)
        self.assertTrue(instance.data_isvalid([['10/10/10', '56']]))
