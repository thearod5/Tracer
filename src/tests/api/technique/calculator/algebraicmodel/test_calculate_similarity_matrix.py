import pandas as pd

from api.technique.variationpoints.algebraicmodel.calculate_similarity_matrix import calculate_similarity_matrix
from tests.res.smart_test import SmartTest


class TestCalculateSimilarityMatrix(SmartTest):
    def test_use_case(self):
        raw_a = pd.Series(["Alex is cool", "Alex sucks a little"])
        raw_b = pd.Series(["Alex is cool", "Alex doesn't sucks but might"])
        similarity_matrix, vocab = calculate_similarity_matrix(raw_a, raw_b)

        assert similarity_matrix[0][0] == 1, similarity_matrix[0][0]
        assert similarity_matrix[0][1] < similarity_matrix[1][1]
