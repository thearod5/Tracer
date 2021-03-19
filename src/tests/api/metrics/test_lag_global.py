import numpy as np

from api.metrics.calculator import calculate_lag, number_of_fp_above_index
from tests.res.smart_test import SmartTest


class TestLag(SmartTest):

    def test_number_of_fp_above_index(self):
        self.assertEqual(0, number_of_fp_above_index([1], 0))
        self.assertEqual(1, number_of_fp_above_index(np.array([0, 1]), 1))
        self.assertEqual(5, number_of_fp_above_index(np.array([0, 0, 0, 0, 0, 1]), 5))

    def test_use_case(self):
        y_true = [1, 0, 1, 0, 1, 1]
        y_pred = [0.8, 0.6, 0.5, 0.4, 0.3, 0.9]
        score = calculate_lag(y_true, y_pred)
        assert score == .75, score

    def test_lag_min(self):
        y_true = [1, 1, 1, 1, 1, 1]
        y_pred = [0.9, 0.8, 0.6, 0.5, 0.4, 0.3]
        score = calculate_lag(y_true, y_pred)
        self.assertEqual(0, score)

    def test_lag_max(self):
        y_true = [0, 0, 0, 0, 0, 1]
        y_pred = [0.9, 0.8, 0.6, 0.5, 0.4, 0.3]
        score = calculate_lag(y_true, y_pred)
        self.assertEqual(5, score)

    def test_lag_no_positives(self):
        y_true = [0, 0, 0, 0, 0, 0]
        y_pred = [0.9, 0.8, 0.6, 0.5, 0.4, 0.3]
        score = calculate_lag(y_true, y_pred)
        self.assertEqual(0, score)
