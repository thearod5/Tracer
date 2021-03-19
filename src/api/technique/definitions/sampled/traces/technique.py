from api.technique.definitions.sampled.artifacts.calculator import SampledArtifactsTechniqueCalculator
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.definitions.sampled.traces.calculator import SampledTracesTechniqueCalculator
from api.technique.parser.itechnique import ITechnique

SAMPLED_TRACED_COMMAND_SYMBOL = "$"


class SampledTracesTechnique(ITechnique):
    def create_definition(self, parameters: [str], components: [str]) -> SampledTechniqueDefinition:
        return SampledTechniqueDefinition(parameters, components)

    def create_calculator(self) -> SampledArtifactsTechniqueCalculator:
        return SampledTracesTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol() -> str:
        return SAMPLED_TRACED_COMMAND_SYMBOL
