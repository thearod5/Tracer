"""
TODO
"""
from api.technique.definitions.sampled.artifacts.calculator import SampledArtifactsTechniqueCalculator
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.parser.itechnique import ITechnique
from api.technique.parser.itechnique_definition import ITechniqueDefinition


class SampledIntermediateTechnique(ITechnique):
    """
    TODO
    """

    def create_definition(self, parameters: [str], components: [str]) -> ITechniqueDefinition:
        """
        TODO
        :param parameters:
        :param components:
        :return:
        """
        return SampledTechniqueDefinition(parameters, components)

    def create_calculator(self) -> SampledArtifactsTechniqueCalculator:
        """
        TODO
        :return:
        """
        return SampledArtifactsTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol() -> str:
        """
        TODO
        :return:
        """
        return SampledTechniqueDefinition.get_symbol()
