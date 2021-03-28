"""
The following module is responsible for providing an class that allows users to:

1. Store a trace matrix with a key
2. Lookup a matrix with a key or its variants
3. Get list of keys
"""
from typing import List

from api.constants.dataset import GraphPath, SimilarityMatrix
from api.datasets.builder.TraceIdMap import TraceIdMap
from api.datasets.builder.trace_matrix import TraceMatrix


class TraceMatrixMap(TraceIdMap[TraceMatrix]):
    """
    Implements a hash table for objects whose keys are trace ids.
    """

    def get_transitive_matrices_in_path(
        self, transitive_path: GraphPath
    ) -> List[SimilarityMatrix]:
        """
        TODO
        :param transitive_path:
        :return:
        """
        matrices_to_multiple = []
        for node_index in range(len(transitive_path) - 1):
            left_node_index = transitive_path[node_index]
            right_node_index = transitive_path[node_index + 1]
            trace_id = "%d-%d" % (left_node_index, right_node_index)
            next_similarity_matrix = self[trace_id].matrix
            matrices_to_multiple.append(next_similarity_matrix)
        return matrices_to_multiple
