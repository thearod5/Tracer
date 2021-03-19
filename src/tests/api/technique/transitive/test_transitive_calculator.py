import numpy as np

from api.cache.cache import Cache
from api.technique.definitions.direct.calculator import DirectTechniqueData
from api.technique.definitions.transitive.calculator import TransitiveTechniqueCalculator, \
    perform_transitive_aggregation_on_component_techniques, TransitiveTechniqueData, \
    perform_transitive_aggregation, append_direct_component_matrices
from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod
from tests.res.test_technique_helper import TestTechniqueHelper, SimilarityMatrixMock


class TestIntermediateCalculationPipeline(TestTechniqueHelper):
    matrices = [np.array([[0, 1, 0]]),
                np.array([[0],
                          [1],
                          [0]]),
                np.array([[0, 1],
                          [0, 0]])]

    """
    IntermediatePipeline
    """

    def test_transitive_pipeline(self):
        counter_func, counter_dict = self.create_counter_func(self.get_transitive_definition().get_name())
        pipeline_funcs = [counter_func, counter_func]
        pipeline = TransitiveTechniqueCalculator(self.get_transitive_definition(), pipeline_funcs)
        pipeline.run_pipeline_on_dataset(self.dataset)
        self.assertEqual(len(pipeline_funcs), counter_dict["value"])

    """
    IndirectTechniqueCalculator
    """

    def test_transitive_technique_calculator_use_case(self):
        calculator = TransitiveTechniqueCalculator(self.get_transitive_definition())
        technique_data = calculator.calculate_technique_data(self.dataset)
        matrix = technique_data.similarity_matrix

        self.assertEqual((1, 3), matrix.shape)

    """
    calculate_technique_data
    """

    def test_calculate_technique_data(self):
        original = Cache.CACHE_ON
        Cache.CACHE_ON = False

        def counter_func(data: DirectTechniqueData):
            data.similarity_matrix = SimilarityMatrixMock()

        pipeline_funcs = [counter_func]
        calculator = TransitiveTechniqueCalculator(self.get_transitive_definition(), pipeline_funcs)
        technique_data = calculator.calculate_technique_data(self.dataset)
        self.assertEqual(self.dataset.name, technique_data.dataset.name)
        self.assertEqual(self.get_transitive_definition().get_name(), technique_data.technique.get_name())
        self.assertIsNotNone(technique_data.similarity_matrix)
        Cache.CACHE_ON = original

    """
    perform_transitive_aggregation
    """

    def test_perform_transitive_aggregation(self):
        data = TransitiveTechniqueData(self.dataset, self.get_traced_transitive_definition())
        append_direct_component_matrices(data)
        perform_transitive_aggregation(data)

        self.assertEqual((1, 3), data.similarity_matrix.shape)
        self.assertEqual(1, data.similarity_matrix[0][0])
        self.assertEqual(0, data.similarity_matrix[0][1])
        self.assertEqual(1, data.similarity_matrix[0][2])

    """
    perform_transitive_aggregation_on_matrices
    """

    def test_perform_transitive_aggregation_on_matrices(self):
        result = perform_transitive_aggregation_on_component_techniques(self.matrices, AggregationMethod.MAX)

        self.assertEqual((1, 2), result.shape)
        self.assertEqual(1, result[0][1])
        self.assertEqual(1, result.sum(axis=1).sum())
