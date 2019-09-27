import datetime
import logging

import pandas as pd
import numpy as np

from app.models import ProfileParamUnitOption
from btk2.settings import DEBUG

log = logging.getLogger(__name__)


def param_unit_opt_dct(unit_opt):
    return {f'unit_{field}': getattr(unit_opt, field)
            for field in ['symbol', 'name', 'param_default',
                          'conversion_factor']}


def get_summary_data(profile):
    fields = ['name', 'upload_fields', 'upload_field_labels', 'ideal_info',
              'ideal_info_url', 'num_values'] + [f'value2_short_label_{i}'
                                                 for i in [1, 2]]
    summary_qs = profile.summary_data()
    return [{
        'parameter': {
            **{field: getattr(obj.parameter, field) for field in fields},
            **param_unit_opt_dct(
                ProfileParamUnitOption.get_unit_option(
                    profile, summary_qs[i].parameter)
            )},
        'data_point': {field: getattr(obj, field)
                       for field in ['date', 'value', 'value2']},
    } for i, obj in enumerate(summary_qs)]


test_data = [
    {'date': '2016-09-04', 'value': 61.2, 'value2': None},
    {'date': '2016-08-29', 'value': 59.8, 'value2': None},
    {'date': '2016-08-09', 'value': 61.7, 'value2': None},
    {'date': '2016-07-29', 'value': 60.2, 'value2': None},
    {'date': '2016-07-17', 'value': 61.7, 'value2': None},
    {'date': '2016-07-11', 'value': 58.2, 'value2': None},
    {'date': '2016-07-09', 'value': 58.3, 'value2': None},
    {'date': '2016-06-21', 'value': 59.7, 'value2': None},
    {'date': '2016-06-14', 'value': 61.2, 'value2': None},
    {'date': '2016-06-09', 'value': 61.5, 'value2': None},
]

# test_data = [
#     {'date': datetime.date(2016, 9, 4), 'value': 61.2, 'value2': None},
#     {'date': datetime.date(2016, 8, 29), 'value': 59.8, 'value2': None},
#     {'date': datetime.date(2016, 8, 9), 'value': 61.7, 'value2': None},
#     {'date': datetime.date(2016, 7, 29), 'value': 60.2, 'value2': None},
#     {'date': datetime.date(2016, 7, 17), 'value': 61.7, 'value2': None},
#     {'date': datetime.date(2016, 7, 11), 'value': 58.2, 'value2': None},
#     {'date': datetime.date(2016, 7, 9), 'value': 58.3, 'value2': None},
#     {'date': datetime.date(2016, 6, 21), 'value': 59.7, 'value2': None},
#     {'date': datetime.date(2016, 6, 14), 'value': 61.2, 'value2': None},
#     {'date': datetime.date(2016, 6, 9), 'value': 61.5, 'value2': None},
#     {'date': datetime.date(2015, 8, 10), 'value': 57.8, 'value2': None}
# ]


# In resp_data - if meets requirements for certain number and frequency of data
# make key e.g. info which has array with key param_name and value is rolling
# mean series (data of date and values)
def get_rolling_mean(start_date, end_date, data_points=None, meta=None):
    """
    :param start_date: str representing first date in the date range
    :param end_date: str representing last date in the date range
    :param data_points: list of dictionaries containing keys 'date' and 'value'
      and whose 'date' keys are within start_date and end_date
    :param meta: dict containing data to include within the returned dicts
    :return: list of dictionaries containing keys 'date' and 'value'
    """
    if not data_points:
        data_points = []
    if not meta:
        meta = {}

    date_range = pd.date_range(start_date, end_date, freq='D')
    dates = pd.Index([pd.Timestamp(dp['date']) for dp in data_points])
    series = pd.Series([dp['value'] for dp in data_points], dates)

    if DEBUG:
        log.info(list(series.dropna()))
        log.info(list(series.reindex(date_range, fill_value=np.NaN).dropna()))

    return [{'date': a.strftime('%Y-%m-%d'),
             'value': round(b, 1),
             **meta} for a, b in
            series.rolling(4, min_periods=2).mean().dropna().iteritems()]
