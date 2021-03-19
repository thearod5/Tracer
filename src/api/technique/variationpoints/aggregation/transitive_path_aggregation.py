import numpy as np

from api.technique.variationpoints.aggregation.aggregation_functions import arithmetic_aggregation_functions
from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod
from api.technique.variationpoints.aggregation.pca_aggregation import aggregate_pca
from api.technique.variationpoints.algebraicmodel import models
from api.technique.variationpoints.algebraicmodel.models import Similarities, SimilarityMatrix
from api.technique.variationpoints.scalers import Scalers


def apply_transitive_aggregation(similarity_matrices,
                                 transitive_path_aggregation: AggregationMethod) -> SimilarityMatrix:
    if transitive_path_aggregation == AggregationMethod.PCA:
        x_train = create_transitive_aggregation_training_data(similarity_matrices)
        similarities: Similarities = aggregate_pca(x_train)
        scaled_similarities = np.apply_along_axis(arr=similarities, axis=0, func1d=Scalers.minmax_scale)
        new_shape = (similarity_matrices.upper.shape[0], similarity_matrices.lower.shape[1])
        return scaled_similarities.reshape(new_shape)

    else:
        similarity_matrix = aggregate_similarity_matrices_with_arithmetic_aggregator(similarity_matrices,
                                                                                     transitive_path_aggregation)
        return similarity_matrix


def aggregate_similarity_matrices_with_arithmetic_aggregator(similarity_matrices: models,
                                                             indirect_aggregation_type: AggregationMethod):
    """
    Returns a single Experiment.Technique.AlgebraicModel containing the aggregated similarity score between every
    top level artifact to the bottom level.
    : similarity_matrices - The set of technique_matrices to aggregate
    : indirect_aggregation_type - How to aggregate the technique_matrices
    : training_data - The technique_data to train Random Forest, if the aggregation type is set to do so
    """

    if indirect_aggregation_type == AggregationMethod.PCA:
        raise Exception("PCA cannot be performed with this function")
    arithmetic_aggregation_function = arithmetic_aggregation_functions[indirect_aggregation_type]
    similarity_matrix = dot_product_with_aggregation(similarity_matrices, arithmetic_aggregation_function)

    return similarity_matrix


def create_transitive_aggregation_training_data(similarity_matrices: models):
    """
    Returns a matrix of the n_top similarities r_c_indirect_scores between a requirement and a class.
    Shape = (n_requirements x n_classes, 10)
    :param: upper {Experiment.Technique.AlgebraicModel} - Requirements x Designs
    :param: lower {Experiment.Technique.AlgebraicModel} - Designs x Classes
    @return {DistanceMatrix} Requirements as rows and Classes as cols
    """
    n_top = similarity_matrices.upper.shape[0]
    n_middle = similarity_matrices.upper.shape[1]
    n_bottom = similarity_matrices.lower.shape[1]

    multiplied_matrices = (similarity_matrices.upper[:, None, :].T * similarity_matrices.lower[:, :, None]).T

    X = np.zeros(shape=(n_top * n_bottom, n_middle))
    for r in range(n_top):  # number of rows (reqs)
        for c in range(n_bottom):
            r_c_indirect_scores = multiplied_matrices[r][c]  # a list of scores, one score for each design
            linear_index = (r * n_bottom) + c
            X[linear_index, :] = r_c_indirect_scores
    return X


def dot_product_with_aggregation(similarity_matrices: models,
                                 aggregation_function):
    upper = similarity_matrices.upper
    lower = similarity_matrices.lower

    n_rows = similarity_matrices.upper.shape[0]
    n_cols = similarity_matrices.lower.shape[1]

    result = np.zeros(shape=(n_rows, n_cols))

    for row_idx in range(n_rows):
        for col_idx in range(n_cols):
            row_col_multiplication = upper[row_idx, :] * lower[:, col_idx].T
            aggregated_score = aggregation_function(row_col_multiplication)
            result[row_idx, col_idx] = aggregated_score
    return result
