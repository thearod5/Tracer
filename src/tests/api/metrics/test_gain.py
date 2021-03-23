import pandas as pd

from api.constants.processing import (
    AP_COLNAME,
    DATASET_COLNAME,
    LAG_COLNAME,
    METRIC_COLNAME,
    RELATIVE_GAIN_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
)
from api.extension.experiment_types import ExperimentTraceType
from api.tables.metric_table import (
    MetricTable,
    calculate_gain,
    calculate_gain_for_scores,
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
        gain = calculate_gain(100, 50, False)
        self.assertEqual(1, gain)

    def test_calculate_gain_with_inverted(self):
        gain = calculate_gain(100, 50, True)
        self.assertEqual(-1, gain)

    """
    calculate_gain_for_scores
    """

    def test_calculate_gain_for_scores(self):
        base_value = 0.5
        gain_values = calculate_gain_for_scores(
            self.data[AP_COLNAME], base_value, False
        )

        self.assertEqual(-1, gain_values[0])
        self.assertEqual(0, gain_values[1])
        self.assertEqual(1, gain_values[2])

    def test_calculate_gain_for_scores_with_inverted(self):
        base_value = 0.5
        gain_values = calculate_gain_for_scores(
            self.data[LAG_COLNAME], base_value, True
        )

        self.assertEqual(1, gain_values[0])
        self.assertEqual(0, gain_values[1])
        self.assertEqual(-1, gain_values[2])

    """
    calculate_gain_for_source
    """

    def test_calculate_gain_for_source(self):
        gain_df = MetricTable(self.data).calculate_gain().table

        gain_df = gain_df.set_index(
            [DATASET_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME, METRIC_COLNAME]
        )

        self.assertEqual(
            1,
            gain_df.loc["FD", ExperimentTraceType.NONE.value, AP_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )
        self.assertEqual(
            0,
            gain_df.loc["FD", ExperimentTraceType.DIRECT.value, AP_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )
        self.assertEqual(
            1,
            gain_df.loc["FD", ExperimentTraceType.NONE.value, LAG_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )
        self.assertEqual(
            0,
            gain_df.loc["FD", ExperimentTraceType.DIRECT.value, LAG_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )

        self.assertEqual(
            3,
            gain_df.loc["AB", ExperimentTraceType.NONE.value, AP_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )
        self.assertEqual(
            0,
            gain_df.loc["AB", ExperimentTraceType.DIRECT.value, AP_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )
        self.assertEqual(
            0.8,
            gain_df.loc["AB", ExperimentTraceType.NONE.value, LAG_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )
        self.assertEqual(
            0,
            gain_df.loc["AB", ExperimentTraceType.DIRECT.value, LAG_COLNAME][
                RELATIVE_GAIN_COLNAME
            ],
        )
