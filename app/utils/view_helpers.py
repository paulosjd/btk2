
import logging

import pandas as pd
import numpy as np

from app.models import ProfileParamUnitOption

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


def get_rolling_mean(data_points, extra=None):
    """
    :param data_points: list of dictionaries containing keys 'date' and 'value'
      and whose 'date' keys are within start_date and end_date
    :param extra: dict containing data to include within the returned dicts
    :return: list of dictionaries containing keys 'date' and 'value'
    """
    if not extra:
        extra = {}
    dp_values = [dp['value'] for dp in data_points]
    dates = pd.Index([pd.Timestamp(dp['date']) for dp in data_points])
    series = pd.Series(dp_values, dates)
    rolling_means = [
        {'date': a.strftime('%Y-%m-%d'),
         'value': round(b, 1),
         **extra} for a, b in
        series.rolling(4, min_periods=2).mean().dropna().iteritems()
    ]
    dp_values2 = [dp['value2'] for dp in data_points if dp.get('value2')]
    if len(dp_values) == len(dp_values2):
        series2 = pd.Series(dp_values2, dates)
        r_means2 = series2.rolling(4, min_periods=2).mean().dropna().iteritems()
        for ind, item in enumerate(r_means2):
            rolling_means[ind].update({'value2': round(item[1], 1)})
            # log.info({extra.get('param_name'): list(series.dropna())})

    return rolling_means


def get_monthly_changes(data_points, extra=None):
    """
    :param data_points: list of dictionaries containing keys 'date' and 'value'
      and whose 'date' keys are within start_date and end_date
    :param extra: dict containing data to include within the returned dicts
    :return: list of dictionaries containing keys 'date' and 'value'
    """
    if not extra:
        extra = {}
    print(data_points)
    dates = pd.Index([pd.Timestamp(dp['date']) for dp in data_points])

    day_diffs = []
    val_diffs = []
    val2_diffs = []
    has_val2 = len([dp['value2'] for dp in data_points
                    if dp.get('value2')]) == len(data_points)

    for i, dp in enumerate(data_points):
        if i > 0:
            day_diffs.append(
                abs((pd.Timestamp(dp['date']) - pd.Timestamp(
                    data_points[i - 1]['date'])).days)
            )
            val_diffs.append(
                dp['value'] - data_points[i - 1]['value']
            )
            if has_val2:
                val2_diffs.append(
                    dp['value2'] - data_points[i - 1]['value2']
                )
    print(day_diffs)
    print(val_diffs)
    print(val2_diffs)






    # return [{'date': a.strftime('%Y-%m-%d'),
    #          'value': round(b, 1),
    #          **extra} for a, b in
    #         series.rolling(4, min_periods=2).mean().dropna().iteritems()]