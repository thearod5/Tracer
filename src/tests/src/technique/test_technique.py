from api.technique.definitions.combined.technique import HybridTechniqueDefinition
from api.technique.definitions.direct.definition import DirectTechniqueDefinition
from api.technique.parser.itechnique_definition import stringify_paths
from tests.res.test_technique_helper import TestTechniqueHelper


class TestTechnique(TestTechniqueHelper):
    def test_use_case(self):
        test_technique: HybridTechniqueDefinition = self.get_combined_definition()
        self.assertEqual(2, len(test_technique.get_component_techniques()))

        component_techniques = test_technique.get_component_techniques()
        t_one: DirectTechniqueDefinition = component_techniques[0]
        t_two: DirectTechniqueDefinition = component_techniques[1]

        self.assertTrue(self.get_direct_definition().get_name(), t_one.get_name())
        self.assertTrue(self.get_transitive_definition().get_name(), t_two.get_name())

    def test_stringify_paths_simple(self):
        paths = [[0, 2]]
        paths_str = stringify_paths(paths)
        self.assertEqual("0-2", paths_str)

    def test_stringify_paths_combined(self):
        paths = [[0, 2], [0, 1, 2]]
        paths_str = stringify_paths(paths)
        self.assertEqual("0-2|0-1-2", paths_str)
