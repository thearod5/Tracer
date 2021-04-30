"""
TODO
"""
from api.datasets.dataset import Dataset
from api.technique.definitions.direct.definition import DirectTechniqueDefinition
from api.technique.parser.data import TechniqueData
from api.technique.parser.itechnique_calculator import ITechniqueCalculator
from api.technique.variationpoints.algebraicmodel.calculate_similarity_matrix import (
    calculate_similarity_matrix_for_nlp_technique,
)
from api.technique.variationpoints.tracetype.trace_type import TraceType


class DirectTechniqueData(TechniqueData):
    """
    TODO
    """

    def __init__(self, dataset: Dataset, technique: DirectTechniqueDefinition):
        super().__init__(dataset, technique)


def create_direct_algebraic_model(data: DirectTechniqueData):
    """
    Directly compares the datasets layers defined in technique with set algebraic model
    :param data: Data describing the technique and dataset to calculate
    :return: None
    """
    assert len(data.technique.artifact_paths) == 2

    if data.technique.trace_type == TraceType.TRACED:
        trace_id = "-".join(list(map(repr, data.technique.artifact_paths)))
        data.similarity_matrix = data.dataset.traced_matrices[trace_id]
    else:
        upper_level_index, lower_level_index = data.technique.artifact_paths
        upper_artifacts = data.dataset.artifacts[upper_level_index]
        lower_artifacts = data.dataset.artifacts[lower_level_index]
        similarity_matrix = calculate_similarity_matrix_for_nlp_technique(
            data.technique.algebraic_model, upper_artifacts, lower_artifacts
        )
        data.similarity_matrix = similarity_matrix


DIRECT_TECHNIQUE_PIPELINE = [create_direct_algebraic_model]


class DirectTechniqueCalculator(ITechniqueCalculator[DirectTechniqueData]):
    """
    TODO
    """

    def __init__(self, technique_definition: DirectTechniqueDefinition, pipeline=None):
        super().__init__(technique_definition, pipeline)
        if pipeline is None:
            pipeline = DIRECT_TECHNIQUE_PIPELINE
        self.pipeline = pipeline

    def create_pipeline_data(self, dataset: Dataset) -> DirectTechniqueData:
        """
        TODO
        :param dataset:
        :return:
        """
        return DirectTechniqueData(dataset, self.definition)
