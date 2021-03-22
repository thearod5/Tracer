import sys

import numpy as np

from api.metrics.calculator import calculate_ap
from tests.res.smart_test import SmartTest

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")


class TestMap(SmartTest):
    def test_basic_100_precision(self):
        y_pred = np.array([0, 1])
        y_true = np.array([0, 1])
        map_score = calculate_ap(y_true, y_pred)
        self.assertEqual(1, map_score)

    def test_basic_na_precision(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y_pred = np.array([1, 1])
            y_true = np.array([0, 0])
            map_score = calculate_ap(y_true, y_pred)
            self.assertTrue(np.isnan(map_score))
