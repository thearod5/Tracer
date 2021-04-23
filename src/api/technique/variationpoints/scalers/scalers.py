"""
TODO
"""
import numpy as np
from sklearn.preprocessing import minmax_scale

from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod


def scale_with_technique(
    scaling_type: ScalingMethod, matrices: [SimilarityMatrix]
) -> [SimilarityMatrix]:
    """
    Scales given matrices using the specified scaling method. See paper for detailed description of the
    theory and details surrounding each scaling type
    :param scaling_type: the scaling method to perform on the matrices
    :param matrices: list of matrices in technique
    :return: list of SimilarityMatrix after being scaled
    """
    if scaling_type == ScalingMethod.INDEPENDENT:
        return independent_scaling(matrices)
    if scaling_type == ScalingMethod.GLOBAL:
        return global_scaling(matrices)
    raise Exception("Unrecognized Scaling type type: ", scaling_type)


def global_scaling(matrices: [SimilarityMatrix]) -> [SimilarityMatrix]:
    """
    Scales the values of each matrix according to the min-max of all matrices given.
    :param matrices: set of matrices to scale
    :return: SimilarityMatrices after having been scaled globally.
    """
    flatten_matrices = list(map(lambda m: m.flatten(), matrices))
    n_matrix_values = list(map(lambda m: m.size, flatten_matrices))
    aggregate_matrix = np.concatenate(flatten_matrices, axis=0)
    scaled_aggregate = scale_matrix(aggregate_matrix)

    scaled_matrices = []
    start_index = 0
    for m_index, _ in enumerate(matrices):
        values_in_matrix = n_matrix_values[m_index]
        end_index = start_index + values_in_matrix
        scaled_values = scaled_aggregate[start_index:end_index]
        scaled_matrix = np.reshape(scaled_values, newshape=matrices[m_index].shape)
        scaled_matrices.append(scaled_matrix)
        start_index = values_in_matrix

    return scaled_matrices


def independent_scaling(matrices: [SimilarityMatrix]) -> [SimilarityMatrix]:
    """
    Returns the independent scaling of upper and lower matrices.
    :param matrices: list of matrices to scale
    :return: list of matrices each scaled to each respective matrix
    """
    scaled_matrices = []
    for matrix in matrices:
        scaled_values = scale_matrix(matrix.flatten())
        scaled_matrix = np.reshape(scaled_values, newshape=matrix.shape)
        scaled_matrices.append(scaled_matrix)

    return scaled_matrices


def scale_matrix(matrix: SimilarityMatrix):
    return minmax_scale(matrix)
