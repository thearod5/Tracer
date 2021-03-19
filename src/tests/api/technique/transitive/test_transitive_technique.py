from api.technique.definitions.transitive.definition import TRANSITIVE_COMMAND_SYMBOL
from api.technique.definitions.transitive.technique import TransitiveTechnique
from tests.res.test_technique_helper import TestTechniqueHelper

n_function_calls = 0


class TestIntermediateTechnique(TestTechniqueHelper):
    def test_use_case(self):
        technique = TransitiveTechnique(self.transitive_parameters, self.transitive_components)
        data = technique.calculate_technique_data(self.dataset)
        self.assertTrue(data.similarity_matrix.sum(axis=1).sum() > 0)

    def test_symbol(self):
        self.assertEqual(TRANSITIVE_COMMAND_SYMBOL, TransitiveTechnique.get_symbol())
