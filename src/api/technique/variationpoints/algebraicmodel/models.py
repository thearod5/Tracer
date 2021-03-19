from enum import Enum
from typing import Union

import numpy as np
from scipy.sparse import csr_matrix

SimilarityMatrix = Union[csr_matrix, np.ndarray]
Similarities = np.ndarray


class AlgebraicModel(Enum):
    LSI = "LSI"
    VSM = "VSM"


class SimilarityMatrices:
    """
    A set of technique_matrices for a dataset containing 1 is two datasets have been traced
    """

    def __init__(self, upper: SimilarityMatrix, lower: SimilarityMatrix):
        self.upper = upper
        self.lower = lower
        self.matrices = [upper, lower]