from tests.res.test_technique_helper import TestTechniqueHelper


class TestITechniqueDefinition(TestTechniqueHelper):
    def test_contains_stochastic_technique(self):
        definition = self.get_combined_definition()
        self.assertFalse(definition.contains_stochastic_technique())
        sampled_definition = self.get_combined_sampled_artifacts_definition()
        self.assertTrue(sampled_definition.contains_stochastic_technique())
