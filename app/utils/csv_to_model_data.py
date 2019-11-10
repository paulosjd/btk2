import csv
from collections import namedtuple
from datetime import date, datetime
from typing import BinaryIO, Optional


class CsvToModelData:
    """ Designed for usage whereby iterate over if validated """
    field_types_map = {'date': date, 'value': float, 'value2': float}

    def __init__(self, csvfile: BinaryIO, meta: dict) -> None:
        """
        :param csvfile: csv file object
        :param meta: dict with processing info
        e.g. {'field_order': ['date', 'value'], 'date_fmt': '%d/%m/%y'}
        """
        self.csvfile = csvfile
        self.meta = meta
        self._model_data = []
        self.error = ''
        assert self.meta.get('field_order')
        assert self.meta.get('date_fmt')

    def __bool__(self):
        if self.is_valid:
            return True
        return False

    def __iter__(self):
        DataObj = namedtuple('CsvDataObj', self.meta.get('field_order'))
        return iter(DataObj(*x) for x in self._model_data)

    def process_csv(self) -> Optional[bool]:
        try:
            fp = self.csvfile.read().decode('ISO-8859-1').splitlines()
        except AttributeError:
            self.error = 'Please check formatting and try again'
            return False
        csv_data = list(csv.reader(fp))
        if self.shape_isvalid(csv_data) and self.data_isvalid(csv_data):
            self._model_data = csv_data

    @property
    def is_valid(self) -> bool:
        if not self._model_data:
            self.process_csv()
        if self._model_data and not self.error:
            return True
        return False

    def shape_isvalid(self, data: list) -> bool:
        """ Performs basic validation and cleaning of the shape of the data.
        :param data list obtained from csv reader
        :return boolean
        """
        self.error = ''
        self.meta['first_row'] = 1

        # Remove any header or unintended trailing row
        try:
            for n in [0, -1]:
                if not any([s.replace('.', '').isdigit() for s in data[n]]):
                    del data[n]
                    if n == 0:
                        self.meta['first_row'] += 1
        except IndexError:
            self.error = 'Please check formatting and try again'
            return False

        if not all([len(row) == len(self.meta.get('field_order'))
                    for row in data]):
            self.error = 'Please check formatting and try again'
            return False

        if not all([all([cell for cell in row]) for row in data]) or not data:
            self.error = 'Uploaded file contains missing data'
            return False

        return True

    def data_isvalid(self, data: list) -> Optional[bool]:
        """ Attempts to cast values into their expected types
        :param data list obtained from csv reader
        :return boolean
        """
        date_fmt = self.meta['date_fmt']
        for row_ind, row in enumerate(data):
            for cell_ind, cell in enumerate(row):
                field = self.meta['field_order'][cell_ind]
                error_row = row_ind + self.meta['first_row']
                if self.field_types_map.get(field) == float:
                    try:
                        cast_val = round(float(data[row_ind][cell_ind]), 2)
                        if cast_val > 10000:
                            self.error = 'Maximum allowable value is 10,000'
                            return
                    except ValueError:
                        self.error = f'Format issue: Column {cell_ind + 1}' \
                                     f' Row {error_row}'
                        return
                    data[row_ind][cell_ind] = cast_val
                elif self.field_types_map.get(field) == date:
                    try:
                        cast_val = datetime.strptime(
                            data[row_ind][cell_ind], date_fmt).date()
                    except ValueError:
                        self.error = f'Column {cell_ind + 1}: date format issue'
                        return
                    data[row_ind][cell_ind] = cast_val
                else:
                    self.error = 'Unrecognized field type'
                    return
        return True
