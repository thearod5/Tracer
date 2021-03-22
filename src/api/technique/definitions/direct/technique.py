"""
TODO
"""
from api.technique.definitions.direct.calculator import DirectTechniqueCalculator
from api.technique.definitions.direct.definition import DirectTechniqueDefinition
from api.technique.parser.itechnique import ITechnique
from api.technique.parser.itechnique_definition import ITechniqueDefinition


class DirectTechnique(ITechnique):
    """
    TODO
    """

    def create_definition(
        self, parameters: [str], components: [str]
    ) -> ITechniqueDefinition:
        return DirectTechniqueDefinition(parameters, components)

    def create_calculator(self) -> DirectTechniqueCalculator:
        return DirectTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol() -> str:
        """
        TODO
        :return:
        """
        return DirectTechniqueDefinition.get_symbol()
