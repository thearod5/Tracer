from api.technique.definitions.direct.definition import DIRECT_COMMAND_SYMBOL
from api.technique.definitions.direct.technique import DirectTechnique
from tests.res.test_technique_helper import TestTechniqueHelper


class TestDirectTechnique(TestTechniqueHelper):
    def test_direct_technique(self):
        technique = DirectTechnique(self.direct_definition[1], self.direct_definition[2])
        technique_data = technique.calculate_technique_data(self.dataset)
        self.assertIsNotNone(technique_data.similarity_matrix)

    def test_direct_technique_get_symbol(self):
        self.assertEqual(DIRECT_COMMAND_SYMBOL, DirectTechnique.get_symbol())
