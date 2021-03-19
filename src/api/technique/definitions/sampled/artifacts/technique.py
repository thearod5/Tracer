from api.technique.definitions.sampled.artifacts.calculator import SampledArtifactsTechniqueCalculator
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.parser.itechnique import ITechnique
from api.technique.parser.itechnique_definition import ITechniqueDefinition


class SampledIntermediateTechnique(ITechnique):
    def create_definition(self, parameters: [str], components: [str]) -> ITechniqueDefinition:
        return SampledTechniqueDefinition(parameters, components)

    def create_calculator(self) -> SampledArtifactsTechniqueCalculator:
        return SampledArtifactsTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol() -> str:
        return SampledTechniqueDefinition.get_symbol()
