import logging
from typing import List

import pandas as pd

log = logging.getLogger(__name__)


def get_rolling_mean(data_points: List[dict], extra=None) -> List[dict]:
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

    return rolling_means
