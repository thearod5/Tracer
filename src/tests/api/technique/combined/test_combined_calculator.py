import numpy as np

from api.technique.definitions.combined.technique import CombinedTechniqueData, CombinedTechniqueCalculator, \
    turn_aggregated_values_into_matrix
from tests.res.test_technique_helper import TestTechniqueHelper, SimilarityMatrixMock


class TestCombinedCalculationPipeline(TestTechniqueHelper):
    """
    CombinedTechniquePipeline
    """

    def test_combined_technique_calculator_with_custom_pipeline(self):
        counter_func, counter_dic = self.create_counter_func(self.combined_technique_name)
        pipeline_funcs = [counter_func, counter_func]
        pipeline = CombinedTechniqueCalculator(self.get_combined_definition(), pipeline_funcs)
        pipeline.run_pipeline_on_dataset(self.dataset)
        self.assertEqual(len(pipeline_funcs), counter_dic["value"])

    """
    CombinedTechniqueCalculator
    """

    def test_combined_technique_calculator(self):
        calculator = CombinedTechniqueCalculator(self.get_combined_definition())
        technique_data = calculator.calculate_technique_data(self.dataset)
        matrix = technique_data.similarity_matrix
        self.assert_valid_fake_dataset_similarity_matrix(matrix)

    def test_combined_technique_calculator_with_mutation(self):
        def counter_func(data: CombinedTechniqueData):
            data.similarity_table = SimilarityMatrixMock()

        pipeline_funcs = [counter_func]
        calculator = CombinedTechniqueCalculator(self.get_combined_definition(), pipeline_funcs)
        sim_table = calculator.calculate_technique_data(self.dataset)
        self.assertIsNotNone(sim_table)

    """
    CombinedTechniqueData
    """

    def test_combined_technique_data(self):
        technique_data = CombinedTechniqueData(self.dataset, self.get_combined_definition())
        self.assertEqual(self.combined_technique_name, technique_data.technique.get_name())
        self.assertEqual(self.d_name, technique_data.dataset.name)

    """
    turn_aggregated_values_into_matrix
    """

    def test_turn_aggregated_values_into_matrix(self):
        reshaped = turn_aggregated_values_into_matrix(self.dataset,
                                                      np.array([1, 2, 3]))
        self.assertEqual((1, 3), reshaped.shape)
