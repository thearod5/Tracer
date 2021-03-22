"""
TODO
"""
from enum import Enum

from api.constants.dataset import SimilarityMatrix


class AlgebraicModel(Enum):
    """
    TODO: Docs
    """

    LSI = "LSI"
    VSM = "VSM"


class SimilarityMatrices:  # pylint: disable=too-few-public-methods
    """
    A set of technique_matrices for a dataset containing 1 is two datasets have been traced
    TODO: Add public method
    """

    def __init__(self, upper: SimilarityMatrix, lower: SimilarityMatrix):
        self.upper = upper
        self.lower = lower
        self.matrices = [upper, lower]
