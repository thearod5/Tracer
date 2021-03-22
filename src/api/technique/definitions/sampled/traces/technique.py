"""
TODO
"""
from api.technique.definitions.sampled.artifacts.calculator import (
    SampledArtifactsTechniqueCalculator,
)
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.definitions.sampled.traces.calculator import (
    SampledTracesTechniqueCalculator,
)
from api.technique.parser.itechnique import ITechnique

SAMPLED_TRACED_COMMAND_SYMBOL = "$"


class SampledTracesTechnique(ITechnique):
    """
    TODO
    """

    def create_definition(
        self, parameters: [str], components: [str]
    ) -> SampledTechniqueDefinition:
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
        return SampledTracesTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol() -> str:
        """
        TODO
        :return:
        """
        return SAMPLED_TRACED_COMMAND_SYMBOL
