"""
Represents constants and types used when parsing datasets.
"""
from typing import Dict, Union, List

import numpy as np
from scipy.sparse import csr_matrix

SimilarityMatrix = Union[csr_matrix, np.ndarray]
Similarities = np.ndarray
TraceId2SimilarityMatrixMap = Dict[
    str, SimilarityMatrix
]  # mapping between trace id and its corresponding SimilarityMatrix as traces

GraphPath = List[int]  # ordered list of vertices representing a pat

TraceId2GraphPathsMap = Dict[str, List[GraphPath]]
