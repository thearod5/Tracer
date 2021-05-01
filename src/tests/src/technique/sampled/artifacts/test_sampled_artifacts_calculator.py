from api.datasets.dataset import Dataset
from api.technique.definitions.sampled.artifacts.calculator import (
    SampledArtifactsTechniqueCalculator,
    sample_matrices,
)
from api.technique.definitions.sampled.technique_data import SampledTechniqueData
from api.technique.definitions.transitive.calculator import (
    append_direct_component_matrices,
)
from tests.res.test_technique_helper import TestTechniqueHelper


class TestSampledArtifactsCalculator(TestTechniqueHelper):
    """
    sample_matrices
    """

    def test_sample_matrices(self):
        data = SampledTechniqueData(
            self.dataset, self.get_sampled_technique_definition()
        )
        append_direct_component_matrices(data)
        sample_matrices(data)

        n_transitive_artifacts = data.transitive_matrices[0].shape[1]
        self.assertEqual(n_transitive_artifacts, data.transitive_matrices[1].shape[0])
        self.assertLess(n_transitive_artifacts, 3)
        self.assertGreaterEqual(n_transitive_artifacts, 1)

    """
    SampledArtifactsTechniqueCalculator
    """

    def test_sampled_transitive_technique_calculator(self):
        calculator = SampledArtifactsTechniqueCalculator(
            self.get_sampled_technique_definition()
        )
        data = calculator.calculate_technique_data(Dataset("SAMPLE_EasyClinic"))
        self.assertGreater(data.similarity_matrix.sum(axis=1).sum(), 0)

    def test_sampled_transitive_technique_calculator_empty_data(self):
        calculator = SampledArtifactsTechniqueCalculator(
            self.get_sampled_technique_definition()
        )
        data = calculator.create_pipeline_data(self.dataset)
        self.assertTrue(isinstance(data, SampledTechniqueData))
        self.assertEqual(self.dataset, data.dataset)
