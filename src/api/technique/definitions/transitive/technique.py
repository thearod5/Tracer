"""
TODO
"""
from api.technique.definitions.transitive.calculator import (
    TransitiveTechniqueCalculator,
)
from api.technique.definitions.transitive.definition import (
    TransitiveTechniqueDefinition,
)
from api.technique.parser.itechnique import ITechnique
from api.technique.parser.itechnique_calculator import ITechniqueCalculator


class TransitiveTechnique(ITechnique):
    """
    TODO
    """

    def create_definition(
        self, parameters: [str], components: [str]
    ) -> TransitiveTechniqueDefinition:
        """
        TODO
        :param parameters:
        :param components:
        :return:
        """
        return TransitiveTechniqueDefinition(parameters, components)

    def create_calculator(self) -> ITechniqueCalculator:
        """
        TODO
        :return:
        """
        return TransitiveTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol():
        """
        TODO
        :return:
        """
        return TransitiveTechniqueDefinition.get_symbol()
