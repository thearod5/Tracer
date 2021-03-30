"""
The following module is responsible for providing an class that allows users to:

1. Store a trace matrix with a key
2. Lookup a matrix with a key or its variants
3. Get list of keys
"""
from typing import List

from api.constants.dataset import GraphPath, SimilarityMatrix
from api.datasets.builder.trace_id_map import TraceIdMap
from api.datasets.builder.trace_matrix import TraceMatrix


class TraceMatrixMap(TraceIdMap[TraceMatrix]):
    """
    Implements a hash table for objects whose keys are trace ids.
    """

    def get_trace_matrices_in_path(
        self, graph_path: GraphPath
    ) -> List[SimilarityMatrix]:
        """
        Returns trace matrices corresponding to the artifact levels in given path.
        For example, given path 0-1-2 the following matrices are returned [0-1, 1-2].
        :param graph_path: list of int corresponding to artifact levels.
        :return: list of trace matrix values
        """
        matrices_to_multiple = []
        for node_index in range(len(graph_path) - 1):
            left_node_index = graph_path[node_index]
            right_node_index = graph_path[node_index + 1]
            trace_id = "%d-%d" % (left_node_index, right_node_index)
            next_similarity_matrix = self[trace_id].matrix
            matrices_to_multiple.append(next_similarity_matrix)
        return matrices_to_multiple
