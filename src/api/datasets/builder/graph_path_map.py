"""
The following module is responsible for providing an class that allows users to:

1. Store a trace matrix with a key
2. Lookup a matrix with a key or its variants
3. Get list of keys
"""
from typing import List

from api.constants.dataset import GraphPath
from api.datasets.builder.TraceIdMap import TraceIdMap


class GraphPathMap(TraceIdMap[List[GraphPath]]):
    """
    Implements a hash table for objects whose keys are trace ids.
    """
