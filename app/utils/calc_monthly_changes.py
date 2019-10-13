import logging

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def get_pc_changes_per_month(mpdd, vdpm, mpdd_ind=0):
    """ Used to get pro rata percentage change per month for range of months
    from pre-processed data which has a different interval i.e. different length
    :param mpdd: list, acronym for months_per_days_diff
    :param vdpm: list, acronym for val_pc_diffs_per_month
    :param mpdd_ind: index position to use with months_per_day_diff on recursion
    :return:
    """
    fraction = 1.0
    assert len(mpdd) == len(vdpm), 'Lengths must be equal'
    if len(mpdd) == mpdd_ind:
        return 0

    if not mpdd[mpdd_ind]:
        return get_pc_changes_per_month(mpdd, vdpm, mpdd_ind=mpdd_ind + 1)

    if mpdd[mpdd_ind] >= fraction:
        mpdd[mpdd_ind] -= fraction
        return vdpm[mpdd_ind] * fraction
    else:
        # mpdd[mpdd_ind] is < fraction
        this_fraction = mpdd[mpdd_ind]
        mpdd[mpdd_ind] = 0
        remainder = fraction - this_fraction
        try:
            month_val = vdpm[mpdd_ind] * this_fraction + \
                   vdpm[mpdd_ind + 1] * remainder
        except IndexError:
            return vdpm[mpdd_ind] * this_fraction
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
    latest_date = pd.Timestamp(data_points[0]['date'])
    day_diffs, month_diffs, val_pc_diffs, val2_pc_diffs = [[] for _ in range(4)]
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

    total_days = sum(day_diffs)
    max_days = pd.Timedelta(days=min(total_days, 750))
    earliest_date = latest_date - max_days
    months = pd.date_range(
        earliest_date, latest_date, freq='M'
    ).strftime("%Y-%b").tolist()[::-1]

    val_pc_diffs_per_month = [val / month_diffs[i] for i, val in
                              enumerate(val_pc_diffs)]
    months_per_days_diff = [pd.Timedelta(days=i) / np.timedelta64(1, 'M')
                            for i in day_diffs]

    val2_pc_diffs_per_month = []
    if has_val2:
        val2_pc_diffs_per_month = [val / month_diffs[i] for i, val in
                                   enumerate(val2_pc_diffs)]

    monthly_changes = []
    for month in months:
        mpdd_cp = months_per_days_diff[:]
        data = {'month': month,
                'value': round(get_pc_changes_per_month(
                    months_per_days_diff, val_pc_diffs_per_month), 1),
                **extra}
        if has_val2:
            data['value2'] = round(get_pc_changes_per_month(
                mpdd_cp, val2_pc_diffs_per_month), 1)
        monthly_changes.append(data)

    return monthly_changes
