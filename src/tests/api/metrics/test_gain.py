import pandas as pd

from api.constants.processing import (
    AP_COLNAME,
    DATASET_COLNAME,
    LAG_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
)
from api.tables.metric_table import (
    calculate_gain,
)
from tests.res.smart_test import SmartTest


class TestGain(SmartTest):
    data = pd.DataFrame()
    data[DATASET_COLNAME] = ["FD"] * 3 + ["AB"] * 3
    data[TRANSITIVE_TRACE_TYPE_COLNAME] = [
        "none",
        "direct",
        "none",
        "none",
        "direct",
        "none",
    ]
    data[AP_COLNAME] = [0, 0.5, 1, 1, 0.5, 2]
    data[LAG_COLNAME] = [0, 0.5, 1, 0.1, 0.5, 0.3]

    """
    calculate_gain
    """

    def test_calculate_gain(self):
        gain = calculate_gain(50, 100, False)
        self.assertEqual(1, gain)

    def test_calculate_gain_with_inverted(self):
        gain = calculate_gain(50, 100, True)
        self.assertEqual(-1, gain)

    """
    calculate_gain_for_source
    
    """

    # TODO: Add updated test
