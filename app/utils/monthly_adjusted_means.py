import logging
from typing import List

from pandas import date_range, Timedelta, Timestamp

log = logging.getLogger(__name__)


def get_interpolated_values(day_diffs, data_points, name):
    values = []
    for ind, n in enumerate(day_diffs):
        lat_val = data_points[ind][name]
        try:
            negative = lat_val < data_points[ind + 1][name]
        except IndexError:
            break
        vpdpd = abs(lat_val - data_points[ind + 1][name]) / n
        for i in range(n):
            values.append(
                (lat_val + vpdpd * i) if negative else (lat_val - vpdpd * i)
            )
        if ind + 1 == len(day_diffs):
            values.append(
                (values[-1] + vpdpd) if negative else (values[-1] - vpdpd)
            )
    return values


def get_monthly_means(data_points: List[dict], extra=None) -> List[dict]:
    """
    :param data_points: list of dictionaries containing keys 'date' and 'value'
      and whose 'date' keys are within start_date and end_date
    :param extra: dict containing data to include within the returned dicts
    :return: list of dictionaries containing keys 'date' and 'value'
    """
    if not extra:
        extra = {}
    if len(data_points) < 2:
        return []
    has_val2 = len([dp['value2'] for dp in data_points
                    if dp.get('value2')]) == len(data_points)

    day_diffs = get_day_diffs(data_points)
    latest_date = Timestamp(data_points[0]['date'])
    latest_date_str = latest_date.strftime("%Y-%b")
    max_days = Timedelta(days=min(sum(day_diffs), 375))
    earliest_date = latest_date - max_days
    months_dt = date_range(
        earliest_date, latest_date, freq='M').tolist()[::-1]
    days_range = date_range(
        earliest_date, latest_date, freq='D').tolist()[::-1]

    values = get_interpolated_values(
        day_diffs, data_points, 'value'
    )
    month_keys = [latest_date_str] + [a.strftime("%Y-%b") for a in months_dt]
    months = get_monthly_values(values, days_range, month_keys)
    months2 = []
    if has_val2:
        values2 = get_interpolated_values(day_diffs, data_points, 'value2')
        months2 = get_monthly_values(values2, days_range, month_keys)

    monthly_means = []
    for k, v in months.items():
        data = {'month': k, 'value': v, **extra}
        if has_val2 and months.keys() == months2.keys():
            data['value2'] = months2[k]
        monthly_means.append(data)

    return monthly_means


def get_monthly_values(values, days_range, month_keys):
    months = {k: [] for k in month_keys}
    for ind, value in enumerate(values):
        try:
            months[days_range[ind].strftime("%Y-%b")].append(value)
        except IndexError:
            break
    for k, v in months.items():
        months[k] = round(sum(v) / len(v), 1)
    return months


def get_day_diffs(data_points):
    day_diffs = []
    for i, dp in enumerate(data_points):
        if i > 0:
            day_diffs.append(
                abs((Timestamp(dp['date']) - Timestamp(
                    data_points[i - 1]['date'])).days)
            )
    return day_diffs
