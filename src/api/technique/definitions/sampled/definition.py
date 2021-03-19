from api.technique.definitions.transitive.definition import TransitiveTechniqueDefinition

SAMPLED_COMMAND_SYMBOL = "~"


class SampledTechniqueDefinition(TransitiveTechniqueDefinition):
    def __init__(self, parameters: [str], components: [str]):
        self.sample_percentage = None
        super().__init__(parameters, components)
        self._is_stochastic = True

    def parse(self):
        super().parse()
        self.sample_percentage = float(self.parameters[2])

    def validate(self):
        assert self.sample_percentage is not None

    @staticmethod
    def get_symbol() -> str:
        return SAMPLED_COMMAND_SYMBOL
