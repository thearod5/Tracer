"""
TODO
"""
import numpy as np
from sklearn.preprocessing import scale

from api.technique.variationpoints.aggregation.aggregation_functions import (
    arithmetic_aggregation_functions,
)
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.aggregation.pca_aggregation import aggregate_pca
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix
from api.technique.variationpoints.scalers.scalers import scale_matrix


def aggregate_techniques(
    technique_similarity_matrices: [SimilarityMatrix],
    aggregation_method: AggregationMethod,
    standardize_scores=True,
) -> SimilarityMatrix:
    """
    Performs an element-wise aggregation on similarity technique_matrices (representing techniques) with given method
    :param technique_similarity_matrices: all the similarity technique_matrices assumed to be of same shape
    :param aggregation_method: the element-wise operations
    :param standardize_scores: whether to standardize scores into unit variance centered around 0
    :return: similarity matrix of the same shape all the ones given after being aggregated
    """

    flatten_matrices = list(
        map(
            lambda sim_scores: sim_scores
            if len(sim_scores) <= 1 or not standardize_scores
            else scale(sim_scores),
            map(lambda m: m.flatten(), technique_similarity_matrices),
        )
    )
    aggregation_data = np.vstack(flatten_matrices).T
    if aggregation_method == AggregationMethod.PCA:
        values = aggregate_pca(aggregation_data)
    else:
        arithmetic_function = arithmetic_aggregation_functions[aggregation_method]
        values = np.apply_along_axis(arithmetic_function, axis=1, arr=aggregation_data)

    if values.max() > 1:
        values = scale_matrix(values)
    return np.reshape(values, newshape=technique_similarity_matrices[0].shape)
