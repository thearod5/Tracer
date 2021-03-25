"""
TODO
"""
from api.technique.parser.itechnique_definition import ITechniqueDefinition
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from api.technique.variationpoints.tracetype.trace_type import TraceType

DIRECT_COMMAND_SYMBOL = "."


class DirectTechniqueDefinition(ITechniqueDefinition):
    """
    TODO
    """

    def __init__(self, parameters: [str], components: [str]):
        self.artifact_paths: [int] = []
        self.algebraic_model: AlgebraicModel = None
        self.scaling_type: ScalingMethod = None
        self.trace_type: TraceType = None
        super().__init__(parameters, components)

    def parse(self):
        """
        TODO
        :return:
        """
        assert (
            len(self.parameters) == 2
        ), "Expected algebraic model and trace type: %d" % len(self.parameters)
        self.algebraic_model = AlgebraicModel(self.parameters[0])
        self.trace_type = TraceType(self.parameters[1])

        if len(self.components) != 2:
            raise Exception("expected (s t) as graph_paths got %s" % self.components)
        self.source_level = int(self.components[0])
        self.target_level = int(self.components[1])
        self.artifact_paths = [self.source_level, self.target_level]

    def validate(self):
        """
        TODO
        :return:
        """
        assert len(self.artifact_paths) == 2
        assert self.algebraic_model is not None
        assert self.trace_type is not None

    @staticmethod
    def get_symbol() -> str:
        """
        TODO
        :return:
        """
        return DIRECT_COMMAND_SYMBOL
