import logging

import numpy as np
import pandas as pd

from app.models import ProfileParamUnitOption

log = logging.getLogger(__name__)


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


# TODO Test where length of ... months is less than len of ...
def get_pc_change_per_month(*args, mpdd_ind=0, val2=False):
    """ Used to get pro rata percentage change per month for range of months
    from pre-processed data which has a different interval i.e. different length
    :param args: first is months_per_day_diffs, second is val_pc_diffs_per_day
    :param mpdd_ind: index position to use on months_per_day_diff
    :return:
    """

    mpdd, val_pc_diffs_per_month = args
    fraction = 1.0
    assert len(mpdd) == len(val_pc_diffs_per_month), 'Lengths must be equal'

    if not mpdd[mpdd_ind]:
        return get_pc_change_per_month(*args, mpdd_ind + 1)

    if mpdd[mpdd_ind] >= fraction:
        mpdd[mpdd_ind] -= fraction
        return val_pc_diffs_per_month[mpdd_ind] * fraction
    else:
        this_fraction = mpdd[mpdd_ind]
        mpdd[mpdd_ind] = 0
        remainder = fraction - this_fraction
        try:
            month_val = val_pc_diffs_per_month[mpdd_ind] * this_fraction + \
                   val_pc_diffs_per_month[mpdd_ind + 1] * remainder
        except IndexError:
            return val_pc_diffs_per_month[mpdd_ind] * fraction
        mpdd[mpdd_ind] = 0
        mpdd[mpdd_ind + 1] -= remainder
        return month_val


def get_monthly_changes(data_points, extra=None):
    """
    :param data_points: list of dictionaries containing keys 'date' and 'value'
      and whose 'date' keys are within start_date and end_date
    :param extra: dict containing data to include within the returned dicts
    :return: list of dictionaries containing keys 'date' and 'value'
    """
    if not extra:
        extra = {}
    if not data_points:
        return
    print(data_points)
    latest_date = pd.Timestamp(data_points[0]['date'])
    day_diffs = []
    month_diffs = []
    val_pc_diffs = []
    val2_pc_diffs = []
    has_val2 = len([dp['value2'] for dp in data_points
                    if dp.get('value2')]) == len(data_points)

    for i, dp in enumerate(data_points):
        if i > 0:
            dp_min1 = data_points[i - 1]
            day_diffs.append(
                abs((pd.Timestamp(dp['date']) - pd.Timestamp(
                    data_points[i - 1]['date'])).days)
            )
            month_diffs.append(
                abs(pd.Timestamp(dp['date']) - pd.Timestamp(
                    data_points[i - 1]['date'])) / np.timedelta64(1, 'M')
            )
            val_pc_diffs.append(
                -((dp['value'] - dp_min1['value']) / dp['value']) * 100
            )



            if has_val2:
                val2_pc_diffs.append(
                    -((dp['value2'] - dp_min1['value2']) / dp['value2']) * 100
                )

    print(day_diffs)
    total_days = sum(day_diffs)
    max_days = pd.Timedelta(days=min(total_days, 750))
    earliest_date = latest_date - max_days
    months = pd.date_range(
        earliest_date, latest_date, freq='M'
    ).strftime("%Y-%b").tolist()[::-1]

    val_pc_diffs_per_day = [val / day_diffs[i] for i, val in
                            enumerate(val_pc_diffs)]
    val_pc_diffs_per_month = [val / month_diffs[i] for i, val in
                              enumerate(val_pc_diffs)]
    val2_pc_diffs_per_day = [val / day_diffs[i] for i, val in
                             enumerate(val2_pc_diffs)]

    print(val_pc_diffs_per_day)
    # print(val2_pc_diffs_per_day)

    months_per_days_diff = [pd.Timedelta(days=i) / np.timedelta64(1, 'M')
                            for i in day_diffs]
    print(months)
    print(months_per_days_diff)
    mpdd_cumsum = np.cumsum(months_per_days_diff)
    print(mpdd_cumsum)
    print(val_pc_diffs_per_day)
    print(val_pc_diffs_per_month)

    # ['2019-Aug', '2019-Jul', '2019-Jun', '2019-May', '2019-Apr', '2019-Mar',
    #  '2019-Feb', '2019-Jan', '2018-Dec', '2018-Nov', '2018-Oct', '2018-Sep',
    #  '2018-Aug', '2018-Jul', '2018-Jun', '2018-May', '2018-Apr', '2018-Mar',
    #  '2018-Feb', '2018-Jan', '2017-Dec', '2017-Nov', '2017-Oct', '2017-Sep',
    #  '2017-Aug']
    # [2.0370028131994498, 2.9897944516314503, 2.464116306289657,
    #  3.4826177128893816, 0.689952565761104, 4.336844699069796,
    #  6.965235425778763, 17.971621593872563, 6.012443787346763]
    # [2.03700281  5.02679726  7.49091357 10.97353128 11.66348385 16.00032855
    #  22.96556397 40.93718557 46.94962936]

    for i in range(len(months)):
        pass

    day_count = 0
    monthly_data = {}
    for month in months:

        pc_diff = 0
        monthly_data[month] = pc_diff

    # return [{'date': a.strftime('%Y-%m-%d'),
    #          'value': round(b, 1),
    #          **extra} for a, b in
    #         series.rolling(4, min_periods=2).mean().dropna().iteritems()]


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