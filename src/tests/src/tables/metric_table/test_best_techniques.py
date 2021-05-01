"""
The following module is responsible for testing the functionality of the metric table
"""
import random
from typing import List

import pandas as pd

from api.constants.processing import (
    AP_COLNAME,
    AUC_COLNAME,
    BEST_TECHNIQUE_AGGREGATE_METRICS,
    DATASET_COLNAME,
    LAG_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
    NAME_COLNAME,
    TECHNIQUE_TYPE_COLNAME,
)
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable
from tests.res.smart_test import SmartTest


class TestGainBetweenMetrics:
    """
    This is responsible that calculating gain across techniques is responsive to
    metrics that need to invert the equation for relative gain.
    """

    technique_ids = [DIRECT_ID, TRANSITIVE_ID, HYBRID_ID]

    TEST_DATASET_NAME = "TEST"
    WORST_TECHNIQUE_SCORES = [0, 0, 0]
    BEST_TECHNIQUE_SCORES = [0.75, 0.75, 0.75]
    expected_values = [1, 1 / 2, 1 / 3]
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

    def test_gain(self):
        metric_table = MetricTable(self.data)
        gain = metric_table.calculate_gain_between_techniques(
            {self.TEST_DATASET_NAME: ("old", "new")}
        )
        print(gain)

    inverted_metrics = [
        {
            DATASET_COLNAME: TEST_DATASET_NAME,
            AP_COLNAME: 0.25,
            AUC_COLNAME: 0.5,
            LAG_NORMALIZED_INVERTED_COLNAME: 0.75,
        },
        {
            DATASET_COLNAME: TEST_DATASET_NAME,
            AP_COLNAME: 0.5,
            AUC_COLNAME: 0.75,
            LAG_NORMALIZED_INVERTED_COLNAME: 1,
        },
    ]
    inverted_data = pd.DataFrame(entries)


class TestFindBestTechnique(SmartTest):
    """
    The following class test finding the best technique for each
    family.
    """

    technique_ids = [DIRECT_ID, TRANSITIVE_ID, HYBRID_ID]
    entries = []
    TEST_DATASET_NAME = "TEST"
    WORST_TECHNIQUE_SCORES = [0, 0, 0]
    BEST_TECHNIQUE_SCORES = [0.75, 0.75, 0.75]

    for t_id in technique_ids:
        worst_entry = {
            DATASET_COLNAME: TEST_DATASET_NAME,
            TECHNIQUE_TYPE_COLNAME: t_id,
            BEST_TECHNIQUE_AGGREGATE_METRICS[0]: WORST_TECHNIQUE_SCORES[0],
            BEST_TECHNIQUE_AGGREGATE_METRICS[1]: WORST_TECHNIQUE_SCORES[1],
            BEST_TECHNIQUE_AGGREGATE_METRICS[2]: WORST_TECHNIQUE_SCORES[2],
        }
        entries.append(worst_entry)

        best_entry = {
            DATASET_COLNAME: TEST_DATASET_NAME,
            TECHNIQUE_TYPE_COLNAME: t_id,
            BEST_TECHNIQUE_AGGREGATE_METRICS[0]: BEST_TECHNIQUE_SCORES[0],
            BEST_TECHNIQUE_AGGREGATE_METRICS[1]: BEST_TECHNIQUE_SCORES[1],
            BEST_TECHNIQUE_AGGREGATE_METRICS[2]: BEST_TECHNIQUE_SCORES[2],
        }
        entries.append(best_entry)

        for i in range(10):
            random_entry = {
                DATASET_COLNAME: TEST_DATASET_NAME,
                TECHNIQUE_TYPE_COLNAME: t_id,
                AP_COLNAME: random.random() * 0.25 + 0.25,
                AUC_COLNAME: random.random() * 0.25 + 0.25,
                LAG_NORMALIZED_INVERTED_COLNAME: random.random() * 0.25 + 0.25,
            }
            entries.append(random_entry)
    data = pd.DataFrame(entries)

    def test_find_best(self):
        """
        Verifies that the best techniques are extracted
        """
        self.assert_technique_extracted("best", self.BEST_TECHNIQUE_SCORES)

    def test_find_worst(self):
        """
        Verifies that the best technique (the one with
        :return:
        """
        self.assert_technique_extracted("worst", self.WORST_TECHNIQUE_SCORES)

    def assert_technique_extracted(self, name: str, expected_scores: List[float]):
        metric_table = MetricTable(self.data)
        for family_name in self.technique_ids:
            table_method = getattr(
                metric_table, f"find_{name}_{family_name.lower()}_techniques"
            )
            technique_query = table_method().table
            self.assertEqual(1, len(technique_query))
            technique_entry = technique_query.iloc[0]
            for m_index, m_name in enumerate(BEST_TECHNIQUE_AGGREGATE_METRICS):
                self.assertEqual(
                    expected_scores[m_index],
                    technique_entry[m_name],
                )
