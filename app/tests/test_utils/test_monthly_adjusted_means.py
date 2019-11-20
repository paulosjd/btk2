from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from pandas import date_range, Timedelta, Timestamp

from app.utils.monthly_adjusted_means import (
    get_interpolated_values, get_monthly_means, get_monthly_values,
    get_day_diffs
)


class MonthlyAdjustedMeansTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.dps_input = [
            {'value': 50.0, 'value2': 59.0, 'date': '2018-12-18'},
            {'value': 52.0, 'value2': 46.0, 'date': '2018-11-10'},
            {'value': 52.0, 'value2': 50.0, 'date': '2018-10-10'},
            {'value': 44.0, 'value2': 61.0, 'date': '2018-09-09'}
        ]

    def test_get_interpolated_values(self):
        days_diffs_input = [38, 31, 31]
        expected_output = []
        for ind, n in enumerate(days_diffs_input):
            lat_val = self.dps_input[ind]['value']
            negative = lat_val < self.dps_input[ind + 1]['value']
            vpdpd = abs(lat_val - self.dps_input[ind + 1]['value']) / n
            for i in range(n):
                expected_output.append(
                    (lat_val + vpdpd * i) if negative else (lat_val - vpdpd * i)
                )
            if ind + 1 == len(days_diffs_input):
                expected_output.append(
                    (expected_output[-1] + vpdpd) if negative
                    else (expected_output[-1] - vpdpd)
                )
        self.assertEqual(
            expected_output,
            get_interpolated_values(days_diffs_input, self.dps_input, 'value')
        )

    def test_get_monthly_means_dps_len_lt_2(self):
        self.assertEqual([], get_monthly_means([{'a': 2}], extra={'b': '3'}))

    @patch('app.utils.monthly_adjusted_means.get_monthly_values')
    @patch('app.utils.monthly_adjusted_means.get_interpolated_values')
    @patch('app.utils.monthly_adjusted_means.get_day_diffs')
    def test_get_monthly_means_not_val2(self, gdd_patch, giv_patch, gmv_patch):
        gmv_patch.return_value = {'feb': 2, 'mar': 5, 'apr': 5}
        gdd_patch.return_value = [38, 31, 31]
        lat_date = Timestamp(self.dps_input[0]['date'])
        earliest_date = Timestamp(lat_date) - Timedelta(
            days=sum(gdd_patch.return_value))
        gdd_patch.return_value = [38, 31, 31]
        months_dt, days_range = [
            date_range(earliest_date, lat_date, freq=s).tolist()[::-1]
            for s in ['M', 'D']
        ]
        for dct in self.dps_input:
            del dct['value2']
        self.assertEqual(
            [{'month': a, 'value': b, 'foo': 'bar'}
             for a, b in gmv_patch.return_value.items()],
            get_monthly_means(self.dps_input, {'foo': 'bar'})
        )
        gmv_patch.assert_called_with(
            giv_patch.return_value, days_range,
            [a.strftime("%Y-%b") for a in [lat_date] + months_dt]
        )

    @patch('app.utils.monthly_adjusted_means.get_monthly_values')
    @patch('app.utils.monthly_adjusted_means.get_interpolated_values')
    @patch('app.utils.monthly_adjusted_means.get_day_diffs')
    def test_get_monthly_means_has_val2(self, gdd_patch, giv_patch, gmv_patch):
        gdd_patch.return_value = [38, 31, 31]
        months, months2 = [dict(zip(['feb', 'mar', 'apr'], lst))
                           for lst in [[2, 4, 5], [4, 2, 4]]]
        gmv_patch.side_effect = [months, months2]
        expected_return_val = [{'month': k, 'value': v, 'value2': months2[k]}
                               for k, v in months.items()]
        self.assertEqual(expected_return_val, get_monthly_means(self.dps_input))

    def test_get_monthly_values(self):
        d_nums = [4, 10, 16, 18, 24]
        ds = len(d_nums)
        values = [4, 3, 5, 5, 7, 8] * ds + [1]  # IndexError to catch and break
        month_keys = [f'2018-{s}' for s in ['Apr', 'May', 'Jun']]  # Apr, so 4
        expected_output = {
            k: round(sum(values[(i-1)*ds:i*ds]
                         ) / len(values[(i-1)*ds:i*ds]), 1)
            for i, k in enumerate(month_keys, 1)
        }
        self.assertEqual(
            expected_output,
            get_monthly_values(
                values,
                [datetime.strptime(f'2018-{b}-{a}', "%Y-%m-%d")
                 for b, _ in enumerate(month_keys, 4) for a in d_nums],
                month_keys
            )
        )



