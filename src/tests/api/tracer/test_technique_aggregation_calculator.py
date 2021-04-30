"""
The following module is responsible for testing that the aggregation (combination) of technique scores
is doing so considering scores may have entirely different meaning and so different ranges
(e.g. negative numbers may be valid for some but invalid in others).
"""
import numpy as np

from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.aggregation.technique_aggregation_calculator import (
    aggregate_techniques,
)
from tests.res.smart_test import SmartTest


class TestTechniqueAggregationCalculator(SmartTest):
    """
    Creates a series of techniques, represented by similarity technique_matrices, and tests the aggregation into a single
    technique.
    """

    similarity_matrix_a = np.array([[0, 1, 0]])
    similarity_matrix_b = np.array([[0, 1, 0]])
    similarity_matrix_c = np.array([[0, 1, 0]])
    technique_matrices = np.array(
        [similarity_matrix_a, similarity_matrix_b, similarity_matrix_c]
    )

    def test_sum(self):
        result = aggregate_techniques(
            self.technique_matrices, AggregationMethod.SUM, standardize_scores=False
        )
        self.assertEqual(self.technique_matrices[0].shape, result.shape)
        self.assertEqual(1, result[0][1])

    def test_pca(self):
        result = aggregate_techniques(
            self.technique_matrices, AggregationMethod.PCA, standardize_scores=False
        )
        self.assertEqual(self.technique_matrices[0].shape, result.shape)
        self.assertEqual(0, result[0][0])
        self.assertEqual(1, result[0][1])
        self.assertEqual(0, result[0][0])
