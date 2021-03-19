from api.technique.definitions.combined.technique import CombinedTechniqueDefinition, create_technique, \
    COMBINED_COMMAND_SYMBOL
from tests.res.test_technique_helper import TestTechniqueHelper


class TestCombinedDefinition(TestTechniqueHelper):
    """
    CombinedTechniqueDefinition
    """

    def test_parse(self):
        definition = CombinedTechniqueDefinition(self.combined_parameters, self.combined_components)
        self.assertEqual(self.combined_aggregation_type, definition.technique_aggregation)

        component_technique = definition.get_component_techniques()
        self.assertEqual(2, len(component_technique))

    def test_symbol(self):
        self.assertEqual(COMBINED_COMMAND_SYMBOL, CombinedTechniqueDefinition.get_symbol())

    def test_parse_with_wrong_parameters(self):
        self.assertRaises(Exception, lambda: CombinedTechniqueDefinition(["GLOBAL"], self.combined_components))

    def test_parse_with_wrong_components(self):
        self.assertRaises(Exception, lambda: CombinedTechniqueDefinition(self.combined_parameters,
                                                                         self.combined_components[:1]))

    """
    create_technique_by_name
    """

    def test_create_technique_by_name(self):
        self.assertRaises(Exception, lambda: create_technique("!", self.combined_parameters, self.combined_parameters))
