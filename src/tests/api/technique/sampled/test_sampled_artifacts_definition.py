from api.technique.definitions.sampled.definition import SampledTechniqueDefinition, SAMPLED_COMMAND_SYMBOL
from tests.res.test_technique_helper import TestTechniqueHelper


class TestSampledArtifactsDefinition(TestTechniqueHelper):
    def test_use_case(self):
        definition = SampledTechniqueDefinition(self.sampled_parameters,
                                                self.sampled_components)

        self.assertTrue(isinstance(definition.sample_percentage, float))
        self.assertEqual(self.sample_percentage, definition.sample_percentage)
        self.assertTrue(definition._is_stochastic)
        self.assertTrue(definition.contains_stochastic_technique())

    def test_get_symbol(self):
        self.assertEqual(SAMPLED_COMMAND_SYMBOL, SampledTechniqueDefinition.get_symbol())

    def test_without_percentage(self):
        self.assertRaises(Exception,
                          lambda: SampledTechniqueDefinition(self.sampled_parameters[:1],
                                                             self.sampled_components))
