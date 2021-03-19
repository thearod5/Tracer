import numpy as np

from api.datasets.dataset import Dataset
from api.technique.definitions.direct.technique import DirectTechnique
from api.technique.definitions.sampled.artifacts.technique import SampledIntermediateTechnique
from api.technique.definitions.sampled.traces.technique import SampledTracesTechnique
from api.technique.definitions.transitive.technique import TransitiveTechnique
from api.technique.parser import itechnique_definition
from api.technique.parser.data import TechniqueData
from api.technique.parser.definition_parser import parse_technique_definition
from api.technique.parser.itechnique import ITechnique
from api.technique.parser.itechnique_calculator import ITechniqueCalculator
from api.technique.parser.itechnique_definition import ITechniqueDefinition
from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod
from api.technique.variationpoints.aggregation.technique_aggregation_calculator import aggregate_techniques
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix

COMBINED_COMMAND_SYMBOL = "o"


class CombinedTechniqueDefinition(ITechniqueDefinition):
    def __init__(self, parameters: [str], components: [str]):
        self.technique_aggregation = None
        self._component_techniques: [itechnique_definition] = []
        super().__init__(parameters, components)

    def parse(self):
        assert len(self.parameters) == 1
        self.technique_aggregation = AggregationMethod(self.parameters[0])

        assert len(self.components) >= 2

        for component in self.components:
            assert len(component) == 3
            new_technique = create_technique(component[0], component[1], component[2])

            if self.source_level == -1 or self.target_level == -1:
                self.source_level = new_technique.definition.source_level
                self.target_level = new_technique.definition.target_level
            else:
                assert self.source_level == new_technique.definition.source_level, \
                    'source level mismatch. expected %d but got %d' % (self.source_level,
                                                                       new_technique.definition.source_level)
                assert self.target_level == new_technique.definition.target_level, \
                    'target level mismatch. expected %d but got %d' % (self.target_level,
                                                                       new_technique.definition.target_level)

            self._component_techniques.append(new_technique)

    def validate(self):
        assert self.technique_aggregation is not None
        assert len(self._component_techniques) > 0

    @staticmethod
    def get_symbol() -> str:
        return COMBINED_COMMAND_SYMBOL

    def get_component_techniques(self) -> [ITechniqueDefinition]:
        return self._component_techniques


def create_technique_by_name(name: str) -> ITechnique:
    technique_expressions = parse_technique_definition(name)

    assert len(
        technique_expressions) == 3, "expected ([command] [parameters] [components]) got %s" % len(
        technique_expressions)
    command, parameters, components = technique_expressions
    return create_technique(command, parameters, components)


class CombinedTechniqueData(TechniqueData):
    def __init__(self, dataset: Dataset, technique: CombinedTechniqueDefinition):
        super().__init__(dataset, technique)


def perform_technique_aggregation(data: CombinedTechniqueData):
    similarity_matrices = []
    for technique in data.technique.get_component_techniques():
        similarity_matrix: SimilarityMatrix = technique.calculate_technique_data(
            data.dataset).get_similarity_matrix()
        similarity_matrices.append(similarity_matrix)

    aggregation_type = data.technique.technique_aggregation
    aggregated_matrix = aggregate_techniques(similarity_matrices, aggregation_type)
    data.similarity_matrix = aggregated_matrix


COMBINED_TECHNIQUE_PIPELINE = [perform_technique_aggregation]


class CombinedTechniqueCalculator(ITechniqueCalculator[CombinedTechniqueData]):
    """
    A technique resulting from the combination of multiple techniques.
    Each each technique should be able to create a similarity matrix between the top and bottom datasets.
    These technique_matrices are combined by applying the aggregation as an element-wise operation on all technique_matrices.
    """

    def __init__(self, technique_definition: CombinedTechniqueDefinition, pipeline=COMBINED_TECHNIQUE_PIPELINE):
        super().__init__(technique_definition, pipeline)
        self.pipeline = pipeline

    def create_pipeline_data(self, dataset: Dataset) -> CombinedTechniqueData:
        return CombinedTechniqueData(dataset, self.definition)


def turn_aggregated_values_into_matrix(dataset: Dataset, values: np.ndarray):
    return np.reshape(values, newshape=(dataset.artifacts.n_top_artifacts, dataset.artifacts.n_bottom_artifacts))


class CombinedTechnique(ITechnique):
    def create_definition(self, parameters: [str], components: [str]) -> CombinedTechniqueDefinition:
        return CombinedTechniqueDefinition(parameters, components)

    def create_calculator(self) -> CombinedTechniqueCalculator:
        return CombinedTechniqueCalculator(self.definition)

    @staticmethod
    def get_symbol() -> str:
        return CombinedTechniqueDefinition.get_symbol()


TECHNIQUES = [DirectTechnique,
              TransitiveTechnique,
              SampledIntermediateTechnique,
              SampledTracesTechnique,
              CombinedTechnique]


def create_technique(command: str, parameters: [str], components: [str]) -> ITechnique:
    for technique in TECHNIQUES:
        if technique.get_symbol() == command:
            return technique(parameters, components)

    raise SyntaxError("Syntax Error: unable to recognize command %s" % command)