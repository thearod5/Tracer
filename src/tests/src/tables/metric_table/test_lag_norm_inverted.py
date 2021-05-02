"""
The following module is responsible for testing the creation of the
normalized and inverted lag metric.
"""

import pandas as pd

from api.constants.processing import (
    DATASET_COLNAME,
    LAG_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
    NAME_COLNAME,
)
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable
from tests.res.smart_test import SmartTest


class TestCreateLagNormInverted(SmartTest):
    """
    This is responsible testing that the normalized and inverted lag scores are done
    by each dataset.
    """

    technique_ids = [DIRECT_ID, TRANSITIVE_ID, HYBRID_ID]

    A_DATASET = "A"
    B_DATASET = "B"
    DATASETS = [A_DATASET, B_DATASET]
    WORST_TECHNIQUE_SCORES = [0, 0, 0]
    BEST_TECHNIQUE_SCORES = [0.75, 0.75, 0.75]
    expected_values = [("best", 1), ("worst", 0)]
    entries = [
        {
            DATASET_COLNAME: A_DATASET,
            NAME_COLNAME: "best",
            LAG_COLNAME: 0.5,
        },
        {
            DATASET_COLNAME: A_DATASET,
            NAME_COLNAME: "worst",
            LAG_COLNAME: 1,
        },
        {
            DATASET_COLNAME: B_DATASET,
            NAME_COLNAME: "best",
            LAG_COLNAME: 0.25,
        },
        {
            DATASET_COLNAME: B_DATASET,
            NAME_COLNAME: "worst",
            LAG_COLNAME: 0.75,
        },
    ]
    data = pd.DataFrame(entries)

    def test_crate_lag_norm_inverted(self):
        metric_table = MetricTable(self.data)
        values = metric_table.create_lag_norm_inverted().table.set_index(
            [DATASET_COLNAME, NAME_COLNAME]
        )
        for d_name in self.DATASETS:
            for name, e_value in self.expected_values:
                value = values.loc[(d_name, name)][LAG_NORMALIZED_INVERTED_COLNAME]
                self.assertEqual(e_value, value)
