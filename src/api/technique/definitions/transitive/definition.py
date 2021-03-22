"""
TODO
"""
from typing import List

from api.technique.definitions.direct.technique import DirectTechnique
from api.technique.parser.itechnique_definition import ITechniqueDefinition
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod

TRANSITIVE_COMMAND_SYMBOL = "x"


def get_algebraic_model(techniques: [DirectTechnique]):
    """
    TODO
    :param techniques:
    :return:
    """
    algebraic_model = None
    for technique in techniques:
        if algebraic_model is None:
            algebraic_model = technique.definition.algebraic_model
        elif algebraic_model != technique.definition.algebraic_model:
            raise ValueError("expected algebraic technique_matrices to be the same")
    return algebraic_model


class TransitiveTechniqueDefinition(ITechniqueDefinition):
    """
    TODO
    """

    def __init__(self, parameters: [str], components: [str]):
        self.algebraic_model: AlgebraicModel = None
        self.scaling_method: ScalingMethod = None
        self.transitive_aggregation: AggregationMethod = None
        self._component_techniques: List[DirectTechnique] = []
        super().__init__(parameters, components)

    def parse(self):
        """
        TODO
        :return:
        """
        assert len(self.parameters) >= 1
        self.transitive_aggregation = AggregationMethod(self.parameters[0])
        self.scaling_method = ScalingMethod(self.parameters[1])

        assert len(self.components) >= 2
        for component in self.components:
            assert len(component) == 3
            technique = DirectTechnique(component[1], component[2])
            self._component_techniques.append(technique)
        self.algebraic_model = get_algebraic_model(self._component_techniques)

        # add source and target levels
        self.source_level = self._component_techniques[0].definition.source_level
        self.target_level = self._component_techniques[-1].definition.target_level

    def validate(self):
        """
        TODO
        :return:
        """
        super().validate()
        assert self.algebraic_model is not None
        assert self.transitive_aggregation is not None
        assert len(self._component_techniques) >= 2, self._component_techniques

    def get_component_techniques(self) -> List[DirectTechnique]:
        """
        TODO
        :return:
        """
        return self._component_techniques

    @staticmethod
    def get_symbol() -> str:
        """
        TODO
        :return:
        """
        return TRANSITIVE_COMMAND_SYMBOL
