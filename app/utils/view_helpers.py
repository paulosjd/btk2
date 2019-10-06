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
              'ideal_info_url', 'id', 'num_values'] + [f'value2_short_label_{i}'
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
