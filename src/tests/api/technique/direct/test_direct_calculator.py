from api.experiment.cache import Cache
from api.technique.definitions.combined.technique import create_technique_by_name
from api.technique.definitions.direct.calculator import DirectTechniqueCalculator, \
    create_direct_algebraic_model, DirectTechniqueData
from api.technique.definitions.direct.definition import DirectTechniqueDefinition
from api.technique.variationpoints.tracetype.trace_type import TraceType
from tests.res.test_technique_helper import TestTechniqueHelper


class DirectCalculator(TestTechniqueHelper):
    t_name = "(. (VSM NT) (0 2))"
    technique = create_technique_by_name(t_name)

    """
    create_direct_algebraic_model
    """

    def test_create_direct_algebraic_model(self):
        technique = create_technique_by_name(self.t_name)
        data = DirectTechniqueData(self.dataset, technique.definition)

        self.assertIsNone(data.similarity_matrix)
        create_direct_algebraic_model(data)
        self.assertIsNotNone(data.similarity_matrix)
        self.assert_valid_fake_dataset_similarity_matrix(data.similarity_matrix)

    def test_create_direct_algebraic_model_with_traces(self):
        technique = DirectTechniqueDefinition(["VSM", "T"], ["0", "2"])
        self.assertEqual(TraceType.TRACED, technique.trace_type)
        data = DirectTechniqueData(self.dataset, technique)

        self.assertIsNone(data.similarity_matrix)
        create_direct_algebraic_model(data)
        self.assertIsNotNone(data.similarity_matrix)
        self.assertEqual(1, data.similarity_matrix[0][0])
        self.assertEqual(0, data.similarity_matrix[0][1])
        self.assertEqual(1, data.similarity_matrix[0][2])

    """
    DirectPipeline
    """

    def test_direct_pipeline(self):
        counter_func, counter_dict = self.create_counter_func(self.t_name)
        pipeline_funcs = [counter_func, counter_func]
        pipeline = DirectTechniqueCalculator(self.get_direct_definition(), pipeline_funcs)
        pipeline.run_pipeline_on_dataset(self.dataset)
        self.assertEqual(len(pipeline_funcs), counter_dict["value"])

    """
    calculate_technique_data
    """

    def test_calculate_technique_data(self):
        calculator = DirectTechniqueCalculator(self.get_direct_definition())
        technique_data = calculator.calculate_technique_data(self.dataset)
        similarity_matrix = technique_data.similarity_matrix
        self.assert_valid_fake_dataset_similarity_matrix(similarity_matrix)

    def test_test_calculate_technique_data_with_custom_pipeline(self):
        original = Cache.CACHE_ON
        Cache.CACHE_ON = False

        def counter_func(data: DirectTechniqueData):
            data.similarity_matrix = -1

        pipeline_funcs = [counter_func]
        calculator = DirectTechniqueCalculator(self.get_direct_definition(), pipeline_funcs)
        technique_data = calculator.calculate_technique_data(self.dataset)
        self.assertEqual(self.technique.get_name(), technique_data.technique.get_name())
        self.assertEqual(self.dataset.name, technique_data.dataset.name)
        self.assertEqual(-1, technique_data.similarity_matrix)
        Cache.CACHE_ON = original
