"""
The following module creates a module responsible for parsing trace matrices using the paths definition
in structure definitions.
"""

import os
from typing import List, Optional

import numpy as np
from igraph import Graph

from api.constants.dataset import (
    TraceId2SimilarityMatrixMap,
)
from api.constants.techniques import ArtifactLevel, N_ITERATIONS_TRACE_PROPAGATION
from api.datasets.builder.TraceIdMap import TraceIdMap
from api.datasets.builder.graph_operations import (
    get_all_paths,
    get_paths_to_complete_graph,
)
from api.datasets.builder.graph_path_map import GraphPathMap
from api.datasets.builder.ibuilder import IBuilder
from api.datasets.builder.structure_definition import DatasetStructure
from api.datasets.builder.trace_matrix import TraceMatrix
from api.datasets.builder.trace_matrix_map import (
    TraceMatrixMap,
)
from api.extension.type_checks import to_string
from api.technique.definitions.transitive.calculator import (
    perform_transitive_aggregation_on_component_techniques,
)
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.aggregation.technique_aggregation_calculator import (
    aggregate_techniques,
)

"""
A Trace Matrix map contains as keys TraceIds and as values a TraceMatrix
A TraceId is a string in the form of [artifact_a_index]-[artifact_b_index]

A TracePathMap is a dict mapping from TraceIds to a list of integers representing
the nodes indices for a certain path
"""


class TraceMatrixBuilder(IBuilder):
    """
    The following module is responsible for creating all trace matrices in a dataset.
    """

    def __init__(
        self,
        structure_definition: Optional[DatasetStructure] = None,
        trace_matrix_map: Optional[TraceMatrixMap] = None,
    ):
        """
        For each possible trace matrix between levels defined in given structure definition, constructs a trace
        matrix containing all possible transitive traces.
        :param structure_definition: structure definition initialize to some dataset
        :param trace_matrix_map: set of trace matrices to be initialized with
        """
        super().__init__()
        self.structure_definition = structure_definition
        self.artifacts = []
        if trace_matrix_map is not None:
            self.trace_matrix_map: TraceMatrixMap = trace_matrix_map
        else:
            self.trace_matrix_map: TraceMatrixMap = TraceMatrixMap()

    def build(self):
        """
        For every combination of nodes, computes all possible trace matrices between them and combines them setting
        it as the final trace matrix.
        :return: None
        """
        self.build_original_trace_matrices()
        self.build_transitive_trace_matrices()
        self.normalize_trace_matrices_iteratively()

    def build_original_trace_matrices(self):
        for trace_id, matrix_path in self.structure_definition[
            DatasetStructure.TRACES_KEY
        ].items():
            a_level, b_level = trace_id.split("-")
            a_index, b_index = int(a_level), int(b_level)

            if matrix_path is None:
                continue

            trace_matrix = TraceMatrix.create_trace_matrix_from_path(
                self.artifacts[a_index]["id"],
                a_index,
                self.artifacts[b_index]["id"],
                b_index,
                matrix_path,
            )

            self.trace_matrix_map[trace_id] = trace_matrix

    def build_transitive_trace_matrices(self):
        n_levels = len(self.artifacts)
        direct_trace_ids: List[str] = self.trace_matrix_map.get_keys()

        dependency_graph = self.create_trace_matrix_dependency_graph()

        # for each undefined path for nodes a and b find all graph_paths between a and b
        missing_graph_paths: GraphPathMap = get_paths_to_complete_graph(
            direct_trace_ids, dependency_graph, n_levels
        )
        transitive_matrix_map: TraceMatrixMap = self.create_matrices_for_paths(
            missing_graph_paths
        )
        self.trace_matrix_map.update(transitive_matrix_map)
        for missing_path_id, _ in missing_graph_paths:  #
            a_index, b_index = TraceIdMap.parse_trace_id(missing_path_id)
            dependency_graph.add_edge(a_index, b_index)

    def normalize_trace_matrices_iteratively(
        self, iterations: int = N_ITERATIONS_TRACE_PROPAGATION
    ):
        """
        For a specified number of iterations, all transitive traces are calculated and added to existing trace matrices.
        :param iterations: How many iterations upon which to calculate and add transitive trace links
        :return: None
        """
        for _ in range(iterations):
            self.normalize_trace_matrices()

    def normalize_trace_matrices(self):
        """
        returns the trace matrix with all transitive and direct graph_paths.
        :return:
        """
        graph = self.create_trace_matrix_dependency_graph()
        direct_path_map: GraphPathMap = GraphPathMap()
        for trace_id in self.trace_matrix_map.get_keys():
            a_index, b_index = TraceIdMap.parse_trace_id(trace_id)
            direct_path_map[trace_id] = get_all_paths(graph, a_index, b_index)
        updated_trace_matrix_map: TraceMatrixMap = self.create_matrices_for_paths(
            direct_path_map
        )
        self.trace_matrix_map.update(updated_trace_matrix_map)

    def export(self, path_to_dataset: str):
        """
        Exports trace built trace matrices to given dataset folder where each matrix file is a .npy file named
        using the matrix's trace id.
        :param path_to_dataset: path to parsed dataset folder
        :return: None
        """
        for trace_id in self.trace_matrix_map.get_keys():
            a_index, b_index = TraceIdMap.parse_trace_id(trace_id)
            matrix_file_name = "%d-%d.npy" % (a_index, b_index)
            matrix_file_path = os.path.join(
                path_to_dataset, "Oracles", "TracedMatrices", matrix_file_name
            )
            matrix = self.trace_matrix_map[trace_id].matrix
            np.save(matrix_file_path, matrix)
            self.export_paths.append(matrix_file_path)

    def create_trace_matrix_dependency_graph(self):
        """
        Creates a graph containing artifact level indices as nodes and edges between them if a trace matrix is
        defined between artifact levels.
        :return: igraph.Graph
        """
        n_levels = len(self.artifacts)
        direct_trace_ids: List[str] = list(
            map(to_string, self.trace_matrix_map.get_keys())
        )
        return TraceMatrixBuilder.create_dependency_graph(direct_trace_ids, n_levels)

    @staticmethod
    def create_dependency_graph(trace_ids, n_levels: int):
        graph = Graph()
        graph.add_vertices(n_levels)
        for matrix_id in trace_ids:
            a_level, b_level = matrix_id.split("-")
            a_index, b_index = int(a_level), int(b_level)
            graph.add_edge(a_index, b_index)
        return graph

    def create_matrices_for_paths(
        self,
        graph_paths_map: GraphPathMap,
    ) -> TraceMatrixMap:
        """
        For given map of trace ids to a list of graph paths, for each trace id calculates the element-wise max
        matrix of all matrices constructed from associated paths.
        :param graph_paths_map: dict containing trace ids as keys and a list of list of integers representing a
        list of graph paths
        :return:
        """
        path_matrix_map: TraceId2SimilarityMatrixMap = self.calculate_matrix_for_paths(
            graph_paths_map
        )
        result_map = TraceMatrixMap()
        for trace_id, path_matrix in path_matrix_map.items():
            a_index, b_index = TraceIdMap.parse_trace_id(trace_id)
            result_map[trace_id] = TraceMatrix(
                a_index,
                self.artifacts[a_index]["id"],
                b_index,
                self.artifacts[b_index]["id"],
                path_matrix,
            )

        return result_map

    def calculate_matrix_for_paths(
        self, graph_paths: GraphPathMap
    ) -> TraceId2SimilarityMatrixMap:
        """
        For each key corresponding to a TraceId a similarity matrix is calculated for each assigned path.
        For all similarity technique_matrices the element-wise max is take to construct the final matrix
        :param graph_paths: TraceIds as keys and list of GraphPaths as values
        :return: dict with TraceIds as keys and SimilarityMatrices as values
        """
        transitive_aggregation = AggregationMethod.MAX
        result_matrices = {}
        for transitive_path_key, transitive_paths in graph_paths:
            transitive_similarity_matrices = []
            for transitive_path in transitive_paths:
                matrices_to_multiply = (
                    self.trace_matrix_map.get_transitive_matrices_in_path(
                        transitive_path
                    )
                )
                transitive_similarity_matrix = (
                    perform_transitive_aggregation_on_component_techniques(
                        matrices_to_multiply, transitive_aggregation
                    )
                )
                transitive_similarity_matrices.append(transitive_similarity_matrix)
            aggregated_matrix = aggregate_techniques(
                transitive_similarity_matrices, transitive_aggregation
            )
            result_matrices[transitive_path_key] = aggregated_matrix
        return result_matrices

    def set_levels(self, levels: List[ArtifactLevel]):
        self.artifacts = levels

    def __getitem__(self, item):
        return self.trace_matrix_map[item]
