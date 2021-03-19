import numpy as np

from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix
from api.technique.variationpoints.scalers.Scalers import scale_with_technique, independent_scaling, global_scaling
from api.technique.variationpoints.scalers.ScalingMethod import ScalingMethod
from tests.res.smart_test import SmartTest


class TestScalers(SmartTest):
    """
    Tests the scaling is resulting in the proper upper and lower values
    """
    upper = np.array([[0.4, 0.3, 0.2]])
    lower = np.array([[0.6], [0.2], [0.4]])
    matrices = (upper, lower)

    single_upper = np.array([[1, 0.5, 0]])
    single_lower = np.array([[1], [0], [0.5]])

    multi_upper = np.array([[0.5, 0.25, 0]])
    multi_lower = np.array([[1], [0], [0.5]])

    """
   tests all cases scale_with_technique
   """

    def test_scale_with_technique_independent(self):
        scaled_matrices = scale_with_technique(ScalingMethod.INDEPENDENT, self.matrices)
        self.assert_matrices_equal(self.single_upper, scaled_matrices[0])
        self.assert_matrices_equal(self.single_lower, scaled_matrices[1])

    def test_scale_with_technique_global(self):
        scaled_matrices = scale_with_technique(ScalingMethod.GLOBAL, self.matrices)
        self.assert_matrices_equal(self.multi_upper, scaled_matrices[0])
        self.assert_matrices_equal(self.multi_lower, scaled_matrices[1])

    def test_scale_with_technique_with_undefined_technique(self):
        try:
            scale_with_technique("hello", self.matrices)  # breaking definitions
        except:
            return
        self.assertFalse(True)

    """
    use case tests cases for independent and global scaling
    """

    def test_independent_scaling(self):
        scaled_matrices = independent_scaling(self.matrices)
        self.assert_matrices_equal(self.single_upper, scaled_matrices[0])
        self.assert_matrices_equal(self.single_lower, scaled_matrices[1])

    def test_global_scaling(self):
        scaled_matrices = global_scaling(self.matrices)
        self.assert_matrices_equal(self.multi_upper, scaled_matrices[0])
        self.assert_matrices_equal(self.multi_lower, scaled_matrices[1])

    def assert_matrices_equal(self,
                              expected_matrix: SimilarityMatrix,
                              matrix: SimilarityMatrix):
        self.assertEqual(matrix.shape, expected_matrix.shape)
        for r in range(matrix.shape[0]):
            for c in range(matrix.shape[1]):
                actual = list(matrix[r])  # one to many
                expected_list = list(expected_matrix[r])
                for e, a in zip(expected_list, actual):
                    self.assertAlmostEqual(e, a, 3)
