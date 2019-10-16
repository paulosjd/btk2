import logging
from collections import Counter, OrderedDict

import numpy as np
import pandas as pd

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
            if negative:
                values.append(lat_val + vpdpd * i)
            else:
                values.append(lat_val - vpdpd * i)
        if ind + 1 == len(day_diffs):
            values.append(values[-1] + vpdpd if negative else - vpdpd)
    return values


def get_monthly_means(data_points, extra=None):
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

    day_diffs, a,b,c = get_diffs(
        data_points, has_val2=False
    )

    latest_date = pd.Timestamp(data_points[0]['date'])
    latest_date_str = latest_date.strftime("%Y-%b")
    max_days = pd.Timedelta(days=min(sum(day_diffs), 375))
    earliest_date = latest_date - max_days
    months_dt = pd.date_range(earliest_date,
                              latest_date, freq='M').tolist()[::-1]
    days_range = pd.date_range(earliest_date,
                               latest_date, freq='D').tolist()[::-1]



    # make a dataframe axis is date_range, col1 if value, col2 is value2,
    # fill in actual values
    # interpolate na values
    # split/subset by month (cast/make new column of dates -> %Y-%m and split on
    # average values within these


    print(day_diffs)
    print(sum(day_diffs))
    print(len(days_range))
    print(earliest_date)
    print(latest_date)



    values = get_interpolated_values(day_diffs, data_points, 'value')
    df_data = {'value': values}
    if has_val2:
        df_data['value2'] = get_interpolated_values(day_diffs, data_points,
                                                    'value2')
    print(len(values))
    print(len(df_data))
    print(len(data_points))
    foo = {k: [] for k in [latest_date_str] + [a.strftime("%Y-%b")
                                               for a in months_dt]}
    months = [a.strftime("%Y-%b") for a in months_dt]
    for ind, value in enumerate(values):
        month_key = days_range[ind].strftime("%Y-%b")
        foo[month_key].append(value)

    print(foo)

    print(len(values))
    print(len(df_data))
    print(len(data_points))

    print(values)

    df = pd.DataFrame(df_data)
    print(df.shape)
    print(df)

    months = [a.strftime("%Y-%b") for a in months_dt]
    monthly_changes = []
    for month in months:
        data = {'month': month,
                # 'value': value,
                'value': 5,
                **extra}

        monthly_changes.append(data)

    return monthly_changes


# def get_pccpm(mpdd, vdpm, mpdd_ind=0):
#     while





def get_diffs(data_points, has_val2):
    day_diffs, month_diffs, val_pc_diffs, val2_pc_diffs = [[] for _ in range(4)]
    for i, dp in enumerate(data_points):
        if i > 0:
            dp_min1 = data_points[i - 1]
            day_diffs.append(
                abs((pd.Timestamp(dp['date']) - pd.Timestamp(
                    data_points[i - 1]['date'])).days)
            )
            val_pc_diffs.append(
                -((dp['value'] - dp_min1['value']) / dp['value']) * 100
            )
            if has_val2:
                val2_pc_diffs.append(
                    -((dp['value2'] - dp_min1['value2']) / dp['value2']) * 100
                )
    return day_diffs, month_diffs, val_pc_diffs, val2_pc_diffs