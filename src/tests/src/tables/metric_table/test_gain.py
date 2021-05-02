"""
The following module is responsible for testing the functionality of the metric table
"""

import pandas as pd

from api.constants.processing import (
    AP_COLNAME,
    AUC_COLNAME,
    DATASET_COLNAME,
    LAG_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
    NAME_COLNAME,
)
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable
from tests.res.smart_test import SmartTest


class TestGainBetweenMetrics(SmartTest):
    """
    This is responsible that calculating gain across techniques is responsive to
    metrics that need to invert the equation for relative gain.
    """

    technique_ids = [DIRECT_ID, TRANSITIVE_ID, HYBRID_ID]

    TEST_DATASET_NAME = "TEST"
    WORST_TECHNIQUE_SCORES = [0, 0, 0]
    BEST_TECHNIQUE_SCORES = [0.75, 0.75, 0.75]
    expected_values = [(AP_COLNAME, 1), (AUC_COLNAME, 1 / 2), (LAG_COLNAME, 1 / 4)]
    entries = [
        {
            DATASET_COLNAME: TEST_DATASET_NAME,
            NAME_COLNAME: "old",
            AP_COLNAME: 0.25,
            AUC_COLNAME: 0.5,
            LAG_COLNAME: 1,
        },
        {
            DATASET_COLNAME: TEST_DATASET_NAME,
            NAME_COLNAME: "new",
            AP_COLNAME: 0.5,
            AUC_COLNAME: 0.75,
            LAG_COLNAME: 0.75,
        },
    ]
    data = pd.DataFrame(entries)

    inverted_entries = [
        {
            DATASET_COLNAME: TEST_DATASET_NAME,
            NAME_COLNAME: "old",
            AP_COLNAME: 0.25,
            AUC_COLNAME: 0.5,
            LAG_NORMALIZED_INVERTED_COLNAME: 0.75,
        },
        {
            DATASET_COLNAME: TEST_DATASET_NAME,
            NAME_COLNAME: "new",
            AP_COLNAME: 0.5,
            AUC_COLNAME: 0.75,
            LAG_NORMALIZED_INVERTED_COLNAME: 1,
        },
    ]
    inverted_data = pd.DataFrame(inverted_entries)
    expected_inverted_values = [
        (AP_COLNAME, 1),
        (AUC_COLNAME, 1 / 2),
        (LAG_NORMALIZED_INVERTED_COLNAME, 1 / 3),
    ]

    def test_gain(self):
        self.assert_scores(self.data, self.expected_values)

    def test_inverted_gain(self):
        self.assert_scores(self.inverted_data, self.expected_inverted_values)

    def assert_scores(self, table, expected_values):
        metric_table = MetricTable(table)
        gain = metric_table.calculate_gain_between_techniques(
            {self.TEST_DATASET_NAME: ("old", "new")}
        ).table
        self.assertEqual(1, len(gain))
        gain_entry = gain.iloc[0]

        for m_name, e_value in expected_values:
            self.assertEqual(e_value, gain_entry[m_name])
