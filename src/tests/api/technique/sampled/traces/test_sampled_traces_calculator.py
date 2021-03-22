import numpy as np

from api.technique.definitions.sampled.technique_data import SampledTechniqueData
from api.technique.definitions.sampled.traces.calculator import (
    sample_transitive_matrices,
    replace_indices_in_matrix,
    filter_array,
    calc_row_col_index,
    copy_values,
)
from api.technique.definitions.transitive.calculator import (
    append_direct_component_matrices,
)
from tests.res.test_technique_helper import TestTechniqueHelper


class TestSampledTracesCalculator(TestTechniqueHelper):
    """
    SampledTracesTechniqueCalculator
    """

    def test_SampledTracesTechniqueCalculator(self):
        data = SampledTechniqueData(
            self.dataset, self.get_sampled_technique_definition()
        )
        append_direct_component_matrices(data)

        self.assertLess(max(map(lambda m: m.max(), data.transitive_matrices)), 1)
        sample_transitive_matrices(data)
        self.assertEqual(max(map(lambda m: m.max(), data.transitive_matrices)), 1)

    """
    replace_indices_in_matrix
    """

    def test_replace_indices_in_matrix(self):
        traced = np.array([[0, 0], [1, 1]])
        calculated = np.array([[42, 42], [0, 0]])
        indices = [0, 1]
        r = replace_indices_in_matrix(indices, calculated, traced)

        assert r[0][0] == 42
        assert r[0][1] == 42
        assert r[1][0] == 1
        assert r[1][1] == 1

    """
    calc_row_col_index
    """

    def test_calc_row_col_index(self):
        self.assertEqual((0, 0), calc_row_col_index(0, 3))
        self.assertEqual((1, 2), calc_row_col_index(5, 3))
        self.assertEqual((0, 2), calc_row_col_index(2, 3))

    """
    filter_array
    """

    def test_filter_array(self):
        good, bad = filter_array([1, 2, 3], lambda v: v < 2)
        self.assertEqual([1], good)
        self.assertEqual([2, 3], bad)

    """
    sample_transitive_matrices
    """
    source_1 = np.array([[1, 1, 1]])
    source_2 = np.array([[1], [1], [1]])

    target_1 = np.array([[0, 0, 0]])
    target_2 = np.array([[0], [0], [0]])

    def test_sample_transitive_matrices_one(self):
        sources = [self.source_1]
        targets = [self.target_1]
        indices = [0, 2]
        matrices = copy_values(sources, targets, indices)

        self.assertEqual(len(sources), len(matrices))

        matrix = matrices[0]
        self.assertEqual(1, matrix[0, 0])
        self.assertEqual(0, matrix[0, 1])
        self.assertEqual(1, matrix[0, 2])

    def test_sample_transitive_matrices_with_two(self):
        sources = [self.source_1, self.source_2]
        targets = [self.target_1, self.target_2]
        indices = [0, 3, 5]
        matrices = copy_values(sources, targets, indices)

        self.assertEqual(len(sources), len(matrices))

        matrix = matrices[0]
        self.assertEqual(1, matrix[0, 0])
        self.assertEqual(0, matrix[0, 1])
        self.assertEqual(0, matrix[0, 2])

        matrix = matrices[1]
        self.assertEqual(1, matrix[0, 0])
        self.assertEqual(0, matrix[1, 0])
        self.assertEqual(1, matrix[2, 0])
