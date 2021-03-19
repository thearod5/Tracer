import numpy as np
import pandas as pd

from api.datasets.dataset import Dataset
from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod
from api.technique.variationpoints.aggregation.transitive_path_aggregation import apply_transitive_aggregation, \
    aggregate_similarity_matrices_with_arithmetic_aggregator, create_transitive_aggregation_training_data, \
    dot_product_with_aggregation
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrices
from tests.res.smart_test import SmartTest


class TestIntermediateAggregation(SmartTest):
    upper = np.array([[1, 2, 3],
                      [8, 9, 10]])  # (1, 10) R->D
    lower = np.array([[1, 2],
                      [2, 3],
                      [3, 4]])  # (10, 2) D-> C
    similarity_matrices = SimilarityMatrices(upper, lower)

    """
    apply_transitive_aggregation
    """

    def test_apply_transitive_aggregation_pca(self):
        dataset = Dataset("MockDataset")
        similarity_matrices = SimilarityMatrices(dataset.traced_matrices["0-1"],
                                                 dataset.traced_matrices["1-2"])
        similarity_matrix = apply_transitive_aggregation(similarity_matrices, AggregationMethod.PCA)
        self.assertEqual((1, 3), similarity_matrix.shape)

    def test_apply_transitive_aggregation_arithmetic(self):
        dataset = Dataset("MockDataset")
        similarity_matrices = SimilarityMatrices(dataset.traced_matrices["0-1"],
                                                 dataset.traced_matrices["1-2"])
        similarity_matrix = apply_transitive_aggregation(similarity_matrices, AggregationMethod.MAX)
        self.assertEqual((1, 3), similarity_matrix.shape)

    """
    aggregate_similarity_matrices_with_arithmetic_aggregator
    """

    def test_aggregate_similarity_matrices_with_arithmetic_aggregator(self):
        result_matrix = aggregate_similarity_matrices_with_arithmetic_aggregator(
            self.similarity_matrices,
            AggregationMethod.MAX)
        result_shape = result_matrix.shape
        self.assertEqual((2, 2), result_shape)
        self.assertEqual(9, result_matrix[0][0])
        self.assertEqual(12, result_matrix[0][1])
        self.assertEqual(30, result_matrix[1][0])
        self.assertEqual(40, result_matrix[1][1])

    def test_aggregate_similarity_matrices_with_arithmetic_aggregato_with_fake_dataset(self):
        dataset = Dataset("MockDataset")
        similarity_matrices = SimilarityMatrices(dataset.traced_matrices["0-1"],
                                                 dataset.traced_matrices["1-2"])
        self.assertRaises(Exception,
                          lambda: aggregate_similarity_matrices_with_arithmetic_aggregator(similarity_matrices,
                                                                                           AggregationMethod.PCA))

    """
    create_indirect_aggregation_training_data
    """

    def test_create_indirect_aggregation_training_data(self):
        n_top = 2
        n_middle = 3
        n_bottom = 2
        expected_shape = ((n_top * n_bottom), n_middle)

        relation_values = [[1, 0],
                           [0, 0]]
        relation_columns = ["C1", "C2"]

        relations = pd.DataFrame(relation_values, columns=relation_columns)
        relations["id"] = ["R1", "R2"]

        similarity_matrices = SimilarityMatrices(self.upper,
                                                 self.lower)
        result = create_transitive_aggregation_training_data(similarity_matrices)
        self.assertEqual(expected_shape, result.shape)
        self.assertTrue(all(result[0, :] == [1, 4, 9]))
        self.assertTrue(all(result[1, :] == [2, 6, 12]))
        self.assertTrue(all(result[2, :] == [8, 18, 30]))
        self.assertTrue(all(result[3, :] == [16, 27, 40]))

    """
    dot_product_with_aggregation
    """

    def test_dot_product_with_aggregation(self):
        relations = pd.DataFrame([[1]])
        relations["id"] = ["RE-42"]
        similarity_matrices = SimilarityMatrices(self.upper, self.lower)
        result = dot_product_with_aggregation(similarity_matrices, max)
        self.assertEqual(9, result[0][0])
        self.assertEqual(12, result[0][1])
        self.assertEqual(30, result[1][0])
        self.assertEqual(40, result[1][1])

    def test_dot_product_with_pca_aggregation_with_sum(self):
        result_matrix = dot_product_with_aggregation(self.similarity_matrices,
                                                     sum)
        self.assertEqual((2, 2), result_matrix.shape)
        self.assertEqual(sum([9, 4, 1]), result_matrix[0][0])
        self.assertEqual(sum([12, 6, 2]), result_matrix[0][1])
        self.assertEqual(sum([30, 18, 8]), result_matrix[1][0])
        self.assertEqual(sum([40, 27, 16]), result_matrix[1][1])

    def test_dot_product_with_aggregation_with_fake_dataset(self):
        dataset = Dataset("MockDataset")
        similarity_matrices = SimilarityMatrices(dataset.traced_matrices["0-1"],
                                                 dataset.traced_matrices["1-2"])
        result = dot_product_with_aggregation(similarity_matrices, max)
        self.assertEqual(1, result[0][0])
        self.assertEqual(0, result[0][1])
        self.assertEqual(1, result[0][2])
