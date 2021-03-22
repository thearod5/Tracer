from api.technique.definitions.direct.definition import (
    DirectTechniqueDefinition,
    DIRECT_COMMAND_SYMBOL,
)
from api.technique.definitions.transitive.definition import (
    TransitiveTechniqueDefinition,
)
from tests.res.test_technique_helper import TestTechniqueHelper


class TestIntermediateDefinition(TestTechniqueHelper):
    def test_parse(self):
        definition = TransitiveTechniqueDefinition(
            self.transitive_technique_definition[1],
            self.transitive_technique_definition[2],
        )
        self.assertEqual(self.transitive_algebraic_model, definition.algebraic_model)
        self.assertEqual(
            self.transitive_aggregation_type, definition.transitive_aggregation
        )

        component_techniques: [
            DirectTechniqueDefinition
        ] = definition.get_component_techniques()
        self.assertEqual(2, len(component_techniques))

        for component in component_techniques:
            self.assertEqual(
                self.transitive_algebraic_model, component.definition.algebraic_model
            )
            self.assertEqual(
                self.transitive_component_trace_type, component.definition.trace_type
            )

    def test_parse_with_wrong_parameters(self):
        self.assertRaises(
            Exception,
            lambda: TransitiveTechniqueDefinition(
                ["VSM", "SUM"], self.transitive_components
            ),
        )

    def test_parse_with_wrong_components(self):
        self.assertRaises(
            Exception,
            lambda: TransitiveTechniqueDefinition(
                self.transitive_parameters, self.transitive_components[:1]
            ),
        )

    def test_parse_with_wrong_algebraic_model(self):
        component_a = [DIRECT_COMMAND_SYMBOL, ["VSM", "GLOBAL", "NT"], ["0", "1"]]
        component_b = [DIRECT_COMMAND_SYMBOL, ["LSI", "GLOBAL", "NT"], ["0", "1"]]
        components = [component_a, component_b]
        self.assertRaises(
            Exception,
            lambda: TransitiveTechniqueDefinition(
                self.transitive_technique_definition[1], components
            ),
        )
