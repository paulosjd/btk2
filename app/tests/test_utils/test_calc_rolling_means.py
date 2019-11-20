from unittest import TestCase

import pandas as pd

from app.utils.calc_rolling_means import get_rolling_mean


class CalcRollingMeansTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.dps = [{'date': '2018-10-11', 'value': 34},
                    {'date': '2018-10-11', 'value': 32},
                    {'date': '2018-10-11', 'value': 26},
                    {'date': '2018-10-11', 'value': 35},
                    {'date': '2018-10-11', 'value': 28}]
        self.dps2 = [{'value2': i + 30, **dct}
                     for i, dct in enumerate(self.dps)]

    def test_get_rolling_mean_data_points_not_has_value2(self):
        dp_values = [dp['value'] for dp in self.dps]
        dates = pd.Index([pd.Timestamp(dp['date']) for dp in self.dps])
        series = pd.Series(dp_values, dates)
        self.assertEqual(
            [{'date': a.strftime('%Y-%m-%d'), 'value': round(b, 1), 'a': '4'}
             for a, b in series.rolling(
                4, min_periods=2).mean().dropna().iteritems()],
            get_rolling_mean(self.dps, {'a': '4'})
        )

    def test_get_rolling_mean_input_dicts_has_value2(self):
        dp_values = [dp['value'] for dp in self.dps2]
        dp_values2 = [dp['value2'] for dp in self.dps2]
        dates = pd.Index([pd.Timestamp(dp['date']) for dp in self.dps2])
        series = pd.Series(dp_values, dates)
        expected_output = [
            {'date': a.strftime('%Y-%m-%d'), 'value': round(b, 1)}
            for a, b in series.rolling(
                4, min_periods=2).mean().dropna().iteritems()]
        series2 = pd.Series(dp_values2, dates)
        r_means2 = series2.rolling(4, min_periods=2).mean().dropna().iteritems()
        for ind, item in enumerate(r_means2):
            expected_output[ind].update({'value2': round(item[1], 1)})
        self.assertEqual(expected_output, get_rolling_mean(self.dps2))
