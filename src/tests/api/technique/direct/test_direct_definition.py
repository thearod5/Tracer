from api.technique.definitions.direct.definition import DirectTechniqueDefinition, DIRECT_COMMAND_SYMBOL
from tests.res.test_technique_helper import TestTechniqueHelper


class TestDirectDefinition(TestTechniqueHelper):

    def test_direct_technique_definition(self):
        definition = DirectTechniqueDefinition(self.direct_definition[1], self.direct_definition[2])
        self.assertEqual(self.direct_algebraic_model, definition.algebraic_model)
        self.assertEqual(self.direct_trace_type, definition.trace_type)
        self.assertEqual([0, 2], definition.artifact_paths)

    def test_direct_technique_definition_without_scaling(self):
        self.assertRaises(Exception, lambda: DirectTechniqueDefinition(["VSM"], ["0", "2"]))

    def test_direct_technique_definition_without_missing_artifact_levels(self):
        self.assertRaises(Exception, lambda: DirectTechniqueDefinition(["VSM", "GLOBAL", "NT"], ["0"]))

    def test_direct_technique_definition_symbol(self):
        self.assertTrue(DIRECT_COMMAND_SYMBOL, DirectTechniqueDefinition.get_symbol())
