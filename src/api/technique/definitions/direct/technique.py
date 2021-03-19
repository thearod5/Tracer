from api.technique.definitions.direct.calculator import DirectTechniqueCalculator
from api.technique.definitions.direct.definition import DirectTechniqueDefinition
from api.technique.parser.itechnique import ITechnique
from api.technique.parser.itechnique_definition import ITechniqueDefinition


class DirectTechnique(ITechnique):
    def create_definition(self, parameters: [str], components: [str]) -> ITechniqueDefinition:
        return DirectTechniqueDefinition(parameters, components)

    def create_calculator(self) -> DirectTechniqueCalculator:
        return DirectTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol() -> str:
        return DirectTechniqueDefinition.get_symbol()
