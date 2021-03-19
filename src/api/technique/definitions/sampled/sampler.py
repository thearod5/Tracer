from typing import List

import math
from numpy.random.mtrand import choice


def sample_indices(n_indices: int, percent: float) -> List[int]:
    n_indices_to_select = math.floor(percent * n_indices)
    selected_indices = choice(range(0, n_indices),
                              size=n_indices_to_select,
                              replace=False)
    return selected_indices
