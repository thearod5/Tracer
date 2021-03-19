from api.technique.definitions.transitive.calculator import TransitiveTechniqueCalculator
from api.technique.definitions.transitive.definition import TransitiveTechniqueDefinition
from api.technique.parser.itechnique import ITechnique
from api.technique.parser.itechnique_calculator import ITechniqueCalculator


class TransitiveTechnique(ITechnique):
    def create_definition(self, parameters: [str], components: [str]) -> TransitiveTechniqueDefinition:
        return TransitiveTechniqueDefinition(parameters, components)

    def create_calculator(self) -> ITechniqueCalculator:
        return TransitiveTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol():
        return TransitiveTechniqueDefinition.get_symbol()
