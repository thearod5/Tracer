import numpy as np
from sklearn.metrics import average_precision_score

from api.metrics.calculator import (
    calculate_auc,
    calculate_lag,
    calculate_metrics_for_scoring_table,
)
from api.metrics.models import ScoringTable
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

    values = np.zeros((6, 2))
    # pred
    values[0, 0] = 0  # r1 * c1
    values[1, 0] = 1  # r2 * c1
    values[2, 0] = 0  # r3 * c1
    values[3, 0] = 0  # r1 * c2
    values[4, 0] = 1  # r2 * c2
    values[5, 0] = 0  # r3 * c2

    # oracle
    values[0, 1] = 0
    values[1, 1] = 1
    values[2, 1] = 1
    values[3, 1] = 0
    values[4, 1] = 1
    values[5, 1] = 1

    n_queries = 2
    query_length = values.shape[0] // n_queries
    a_query_map = average_precision_score(
        values[:query_length, 1], values[:query_length, 0]
    )
    a_query_auc = calculate_auc(values[:query_length, 1], values[:query_length, 0])
    a_query_lag = calculate_lag(values[:query_length, 1], values[:query_length, 0])

    b_query_map = average_precision_score(
        values[query_length:, 1], values[query_length:, 0]
    )
    b_query_auc = calculate_auc(values[query_length:, 1], values[query_length:, 0])
    b_query_lag = calculate_lag(values[query_length:, 1], values[query_length:, 0])

    def test_single_metrics(self):
        scoring_table = ScoringTable(self.values[:, 0], self.values[:, 1])
        query_metrics = calculate_metrics_for_scoring_table(
            scoring_table, self.n_queries
        )
        self.assertEqual(self.n_queries, len(query_metrics))

        self.assertEqual(self.a_query_map, query_metrics[0].ap)
        self.assertEqual(self.a_query_auc, query_metrics[0].auc)
        self.assertEqual(self.a_query_lag, query_metrics[0].lag)

        self.assertEqual(self.b_query_map, query_metrics[1].ap)
        self.assertEqual(self.b_query_auc, query_metrics[1].auc)
        self.assertEqual(self.b_query_lag, query_metrics[1].lag)
