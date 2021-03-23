"""
This file represents the container for constants related to parsing the technique definition language (TDL)
"""
from typing import List

import numpy as np
import pandas as pd

TECHNIQUE_DELIMITER = "|"
LEVELS_DELIMITER = "-"
UNDEFINED_TECHNIQUE = "NA"
LevelIndices = List[int]
ArtifactPathType = List[LevelIndices]
ArtifactLevel = pd.DataFrame
DIRECT_ID = "DIRECT"
TRANSITIVE_ID = "TRANSITIVE"
COMBINED_ID = "COMBINED"
N_ITERATIONS_TRACE_PROPAGATION: int = 5
SIMILARITY_MATRIX_EXTENSION = ".npy"
SimilaritiesType = np.ndarray
