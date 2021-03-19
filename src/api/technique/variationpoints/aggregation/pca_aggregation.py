import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from api.technique.variationpoints.algebraicmodel.models import Similarities


def get_weights(matrix):
    """
    Given a matrix containing artifact combinations as rows and techniques as CACHE_COLUMNS,
    Returns the weight of each technique.
    """
    n_cols = matrix.shape[1]
    scaled_matrix = np.apply_along_axis(arr=matrix, func1d=scale, axis=0)
    pca_model = PCA(n_components=n_cols, random_state=42)  # keeps all the components
    pca_model.fit(scaled_matrix)
    lambda_values = pca_model.explained_variance_ratio_
    if any(np.isnan(lambda_values)):
        lambda_values = [1 / n_cols] * n_cols
    assert len(lambda_values) == n_cols
    assert len(lambda_values) == n_cols, 'variance values dimension mismatch'
    return lambda_values


def aggregate_pca(x_test) -> Similarities:
    """
    Returns the predictions on x_test after training on x_train and y_train.
    """
    weights = get_weights(x_test)
    return np.apply_along_axis(arr=x_test, func1d=lambda arr: sum(arr * weights), axis=1)
