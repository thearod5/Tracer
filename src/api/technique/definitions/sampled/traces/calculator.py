"""
TODO
"""
from typing import List, Callable

import numpy as np

from api.datasets.dataset import Dataset
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.definitions.sampled.sampler import sample_indices
from api.technique.definitions.sampled.technique_data import SampledTechniqueData
from api.technique.definitions.transitive.calculator import TransitiveTechniqueCalculator, \
    INTERMEDIATE_TECHNIQUE_PIPELINE
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix


def replace_indices_in_matrix(indices_to_replace, source, target):
    """
    Returns calculated_matrix with given indices replaced with values form traced matrix
    in no_indices marked with 0 (Tested with TestFillIndices)
    :param indices_to_replace: {Listof Int} the indices that should
    :param source: A similarity matrix of given shape already containing values
     :param target: The shape of the output matrix
    :return: {Experiment.Technique.SimilarityMatrix} store_matrix with given indices copied from source_matrix
    """
    assert target.shape == source.shape

    target_copy = target.copy()
    n_cols = target.shape[1]
    for index in np.fromiter(indices_to_replace, dtype=int):
        row_index, col_index = calc_row_col_index(index, n_cols)
        target_copy[row_index][col_index] = source[row_index][col_index]
    return target_copy


def calc_row_col_index(index, n_cols):
    """
    TODO
    :param index:
    :param n_cols:
    :return:
    """
    return index // n_cols, index % n_cols


def filter_array(lst: [int], cond: Callable[[int], bool]):
    """
    TODO
    :param lst:
    :param cond:
    :return:
    """
    good = []
    bad = []
    for value in lst:
        if cond(value):
            good.append(value)
        else:
            bad.append(value)
    return good, bad


def get_n_values_in_matrices(matrices: List[SimilarityMatrix]) -> int:
    """
    TODO
    :param matrices:
    :return:
    """
    n_values = 0
    for matrix in matrices:
        n_values = matrix.shape[0] * matrix.shape[1]
        n_values = n_values + n_values
    return n_values


def sample_transitive_matrices(technique_data: SampledTechniqueData):
    """
    For each transitive matrix in given data
    :param technique_data: the data associated for some sampled technique
    :return: None - transitive matrices are updated with the sampled versions.
    """
    n_values = get_n_values_in_matrices(technique_data.transitive_matrices)
    selected_indices = sample_indices(n_values, technique_data.technique.sample_percentage)

    sources = []
    targets = []
    for matrix_index in range(len(technique_data.transitive_matrices)):
        transitive_matrix = technique_data.transitive_matrices[matrix_index]

        top_level, bottom_level = technique_data.technique.get_component_techniques()[
            matrix_index].definition.artifact_paths
        trace_matrix = technique_data.dataset.traced_matrices["%d-%d" % (top_level, bottom_level)]

        sources.append(trace_matrix)
        targets.append(transitive_matrix)
    technique_data.transitive_matrices = copy_values(sources, targets, selected_indices)


def copy_values(sources: List[SimilarityMatrix],
                targets: List[SimilarityMatrix],
                indices: List[int]) -> List[SimilarityMatrix]:
    """
    For each source-target pair, copies the indices within range from source to target.
    :param sources: a list of source matrices representing the original values being copied
    :param targets: a list of target matrices representing the recipients of copied values
    :param indices: a list of indices taken from the collective of all transitive matrices in row-major order
    representing the positions in the matrices that will be copied.
    :return: a list of similarity matrices based on the given target list with the replacement values.
    """
    assert len(sources) == len(targets)

    sampled_matrices = []
    indices_remaining = indices.copy()
    for source, target in zip(sources, targets):
        assert source.shape == target.shape

        n_values_in_matrix = target.shape[0] * target.shape[1]
        boundary_indices, other_indices = filter_array(indices_remaining,
                                                       lambda v, limit=n_values_in_matrix: v < limit)
        sampled_matrix = replace_indices_in_matrix(boundary_indices, source, target)
        sampled_matrices.append(sampled_matrix)
        indices_remaining = [i - n_values_in_matrix for i in other_indices]

    return sampled_matrices


SAMPLED_TRACES_PIPELINE = INTERMEDIATE_TECHNIQUE_PIPELINE.copy()
SAMPLED_TRACES_PIPELINE.insert(1, sample_transitive_matrices)


class SampledTracesTechniqueCalculator(TransitiveTechniqueCalculator):
    """
    TODO
    """

    def __init__(self, definition: SampledTechniqueDefinition):
        super().__init__(definition, SAMPLED_TRACES_PIPELINE)

    def create_pipeline_data(self, dataset: Dataset) -> SampledTechniqueData:
        """
        TODO
        :param dataset:
        :return:
        """
        return SampledTechniqueData(dataset, self.definition)
