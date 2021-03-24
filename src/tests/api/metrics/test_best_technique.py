import pandas as pd

from api.constants.processing import (
    ALGEBRAIC_MODEL_COLNAME,
    AP_COLNAME,
    DATASET_COLNAME,
    LAG_COLNAME,
    PERCENT_BEST_COLNAME,
    RANK_COLNAME,
    TECHNIQUE_COLNAME,
    TRANSITIVE_SCALING_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
)
from api.constants.techniques import DIRECT_ID
from api.tables.metric_table import MetricTable
from tests.res.smart_test import SmartTest


def create_entry(dataset):
    return {
        DATASET_COLNAME: dataset,
        TRANSITIVE_TRACE_TYPE_COLNAME: DIRECT_ID,
        ALGEBRAIC_MODEL_COLNAME: "VSM",
        AP_COLNAME: 0.5,
        LAG_COLNAME: 0.5,
    }


class TestBestTechnique(SmartTest):
    """
    Tests that we can rank based on groups of dataset and trace type. The following data is structured with the
    following features:
    1. Two datasets where first four rows are D1, the latter four are D2
    2. For each dataset, first two rows are traced to T1 and the latter two to T2.
    3. Each trace type contains metrics for both scaling methods (e.g. M1, M2)
    4. D1 ranks M2 highest across all trace types, and D2 ranks M1 highest across all trace types
    """

    data = pd.DataFrame()
    data[DATASET_COLNAME] = ["D1", "D1", "D1", "D1", "D2", "D2", "D2", "D2"]
    data[TRANSITIVE_TRACE_TYPE_COLNAME] = [
        "T1",
        "T1",
        "T2",
        "T2",
        "T1",
        "T1",
        "T2",
        "T2",
    ]
    data[TRANSITIVE_SCALING_COLNAME] = ["M1", "M2"] * 4
    data[AP_COLNAME] = [1, 2, 1, 2, 2, 1, 2, 1]

    def test_create_ranks_with_all_datasets(self):
        """
        Tests that ranks are accurate in respect to dataset x trace type groups.
        :return: None
        """
        ranked_table = MetricTable(self.data).create_ranks().table
        self.assertTrue(RANK_COLNAME in ranked_table.columns)

        self.assertEqual(2, ranked_table[RANK_COLNAME][0])
        self.assertEqual(1, ranked_table[RANK_COLNAME][1])
        self.assertEqual(2, ranked_table[RANK_COLNAME][2])
        self.assertEqual(1, ranked_table[RANK_COLNAME][3])
        self.assertEqual(1, ranked_table[RANK_COLNAME][4])
        self.assertEqual(2, ranked_table[RANK_COLNAME][5])
        self.assertEqual(1, ranked_table[RANK_COLNAME][6])
        self.assertEqual(2, ranked_table[RANK_COLNAME][7])

    def test_create_ranks_with_single_dataset(self):
        """
        Tests that ranks are accurate in respect to data containing a single dataset
        with no dataset column.
        :return: None
        """
        single_dataset = self.data.iloc[:4].drop(DATASET_COLNAME, axis=1)
        ranked_table = MetricTable(single_dataset).create_ranks().table

        self.assertEqual(2, ranked_table[RANK_COLNAME][0])
        self.assertEqual(1, ranked_table[RANK_COLNAME][1])
        self.assertEqual(2, ranked_table[RANK_COLNAME][2])
        self.assertEqual(1, ranked_table[RANK_COLNAME][3])

    def test_percent_best(self):
        """
        Tests that for each trace_type (T1, T2), each scaling method (M1, M2) vote is distributed equally
        among both datasets as displayed in the data.
        :return:
        """
        percent_best_table = MetricTable(self.data).calculate_percent_best().table
        percent_best_table = percent_best_table.set_index(
            [TRANSITIVE_TRACE_TYPE_COLNAME, TECHNIQUE_COLNAME]
        )

        self.assertEqual(4, len(percent_best_table))
        self.assertEqual(
            0.5, percent_best_table.loc[("T1", "M1")][PERCENT_BEST_COLNAME]
        )
        self.assertEqual(
            0.5, percent_best_table.loc[("T1", "M2")][PERCENT_BEST_COLNAME]
        )
        self.assertEqual(
            0.5, percent_best_table.loc[("T2", "M1")][PERCENT_BEST_COLNAME]
        )
        self.assertEqual(
            0.5, percent_best_table.loc[("T2", "M2")][PERCENT_BEST_COLNAME]
        )
