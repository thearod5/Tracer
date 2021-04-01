from api.technique.definitions.combined.technique import (
    create_technique,
    CombinedTechnique,
    HYBRID_COMMAND_SYMBOL,
)
from api.technique.definitions.direct.definition import DIRECT_COMMAND_SYMBOL
from api.technique.definitions.direct.technique import DirectTechnique
from tests.res.test_technique_helper import TestTechniqueHelper

n_function_calls = 0


class TestCombinedTechnique(TestTechniqueHelper):
    """
    CombinedTechnique
    """

    def test_combined_technique(self):
        combined_technique = CombinedTechnique(
            ["SUM"], [self.direct_definition, self.transitive_technique_definition]
        )
        self.assertEqual(HYBRID_COMMAND_SYMBOL, combined_technique.get_symbol())

    """
    parse_technique
    """

    def test_parse_techniques(self):
        technique = create_technique(DIRECT_COMMAND_SYMBOL, ["VSM", "NT"], ["0", "2"])
        self.assertTrue(isinstance(technique, DirectTechnique))

    def test_parse_techniques_unknown_symbol(self):
        self.assertRaises(
            Exception, lambda: create_technique("!", ["VSM", "NT"], ["0", "2"])
        )
