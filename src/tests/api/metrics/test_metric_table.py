import os

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from api.datasets.dataset import Dataset
from api.metrics.calculator import (
    calculate_auc,
    calculate_lag,
    calculate_metrics_for_scoring_table,
)
from api.metrics.models import Table, ScoringTable
from api.technique.definitions.transitive.definition import (
    TransitiveTechniqueDefinition,
)
from tests.res.smart_test import SmartTest


class TestMetricTable(SmartTest):
    t_name = "(x (SUM GLOBAL) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))"
    component_a = [".", ["VSM", "NT"], [0, 1]]
    component_b = [".", ["VSM", "NT"], [1, 2]]

    technique = TransitiveTechniqueDefinition(
        ["SUM", "GLOBAL"], [component_a, component_b]
    )

    d_name = "MockDataset"
    dataset = Dataset(d_name)

    export_path = ".."

    values = np.zeros((3, 2))
    # pred
    values[0, 0] = 0
    values[1, 0] = 1
    values[2, 0] = 0

    # oracle
    values[0, 1] = 0
    values[1, 1] = 1
    values[2, 1] = 1

    n_queries = 1

    expected_map = average_precision_score(values[:, 1], values[:, 0])
    expected_auc = calculate_auc(values[:, 1], values[:, 0])
    expected_lag = calculate_lag(values[:, 1], values[:, 0])

    def test_metric_table(self):
        scoring_table = ScoringTable(self.values[:, 0], self.values[:, 1])
        metrics = calculate_metrics_for_scoring_table(scoring_table, self.n_queries)

        test_file_name = "test.csv"
        export_path = os.path.join(self.export_path, test_file_name)
        if os.path.exists(export_path):
            os.remove(export_path)

        table = Table()
        table.add(metrics)

        # test export
        self.assertFalse(os.path.exists(export_path))
        table.export(export_path)
        self.assertTrue(os.path.exists(export_path))
        df = pd.read_csv(export_path)
        self.assertEqual(1, len(df))
        self.assertEqual(self.expected_lag, df.iloc[0]["lag"])

        os.remove(export_path)

    def test_metrics(self):
        scoring_table = ScoringTable(self.values[:, 0], self.values[:, 1])
        query_metrics = calculate_metrics_for_scoring_table(
            scoring_table, self.n_queries
        )
        mt = query_metrics[0]
        self.assertEqual(self.expected_lag, mt.lag, "lag")
        self.assertEqual(self.expected_map, mt.ap, "map")
        self.assertEqual(self.expected_auc, mt.auc, "auc")
