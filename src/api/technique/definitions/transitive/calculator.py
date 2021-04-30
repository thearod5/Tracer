"""
TODO
"""

from api.datasets.dataset import Dataset
from api.technique.definitions.direct.calculator import DirectTechniqueCalculator
from api.technique.definitions.transitive.definition import (
    TransitiveTechniqueDefinition,
)
from api.technique.parser.data import TechniqueData
from api.technique.parser.itechnique_calculator import ITechniqueCalculator
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.aggregation.transitive_path_aggregation import (
    apply_transitive_aggregation,
)
from api.technique.variationpoints.algebraicmodel.models import (
    SimilarityMatrices,
    SimilarityMatrix,
)
from api.technique.variationpoints.scalers.scalers import (
    scale_with_technique,
)


class TransitiveTechniqueData(TechniqueData):
    """
    TODO
    """

    def __init__(self, dataset: Dataset, technique: TransitiveTechniqueDefinition):
        super().__init__(dataset, technique)
        self.transitive_matrices: [SimilarityMatrix] = []
        self.technique: TransitiveTechniqueDefinition = technique


def append_direct_component_matrices(technique_data: TransitiveTechniqueData):
    """
    Appends a similarity matrix for each artifact layer pair in the transitive technique.
    Each similarity matrix is a direct textual comparison between layers whose algebraic model
    is determined by the transitive technique algebraic model.
    :param technique_data: the technique_data associated with some transitive technique.
    :return: None - the technique technique_data `transitive_matrices` is modified.
    """
    for technique in technique_data.technique.get_component_techniques():
        direct_calculator = DirectTechniqueCalculator(technique.definition)
        similarity_matrix = direct_calculator.calculate_technique_data(
            technique_data.dataset
        ).similarity_matrix
        technique_data.transitive_matrices.append(similarity_matrix)


def perform_transitive_aggregation(data: TransitiveTechniqueData):
    """
    TODO
    :param data:
    :return:
    """
    data.similarity_matrix = perform_transitive_aggregation_on_component_techniques(
        data.transitive_matrices, data.technique.transitive_aggregation
    )


def scale_transitive_matrices(data: TransitiveTechniqueData):
    """
    TODO
    :param data:
    :return:
    """
    data.transitive_matrices = scale_with_technique(
        data.technique.scaling_method, data.transitive_matrices
    )


def perform_transitive_aggregation_on_component_techniques(
    matrices: [SimilarityMatrix], aggregation_type: AggregationMethod
):
    """
    TODO
    :param matrices:
    :param aggregation_type:
    :return:
    """
    aggregate_matrix = matrices[0]
    for similarity_matrix_index in range(1, len(matrices)):
        matrix_b = matrices[similarity_matrix_index]
        similarity_matrix_pair = SimilarityMatrices(aggregate_matrix, matrix_b)
        aggregate_matrix = apply_transitive_aggregation(
            similarity_matrix_pair, aggregation_type
        )
    return aggregate_matrix


TRANSITIVE_TECHNIQUE_PIPELINE = [
    append_direct_component_matrices,
    scale_transitive_matrices,
    perform_transitive_aggregation,
]


class TransitiveTechniqueCalculator(ITechniqueCalculator[TransitiveTechniqueData]):
    """
    A technique resulting from the combination of multiple datasets.
    For artifact layers l0, l1, ..., ln this technique calculates the matrix multiplication result of:
    l0-l1 x l1-l2 x ... x ln-1-ln for n artifact layers. The multiplication is modified so that instead of
    summing the col-row element multiplication results we use the defined aggregator in the technique.
    """

    def __init__(
        self, technique_definition: TransitiveTechniqueDefinition, pipeline=None
    ):
        super().__init__(technique_definition, pipeline)
        if pipeline is None:
            pipeline = TRANSITIVE_TECHNIQUE_PIPELINE
        self.pipeline = pipeline

    def create_pipeline_data(self, dataset: Dataset) -> TransitiveTechniqueData:
        return TransitiveTechniqueData(dataset, self.definition)
