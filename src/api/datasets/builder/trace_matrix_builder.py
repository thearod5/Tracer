"""
The following module creates a module responsible for parsing trace matrices using the paths definition
in structure definitions.

A Trace Matrix Dependency Graph is a graph where the nodes correspond to artifact levels in a dataset and where
edges exist if a trace matrix between.

Note, this graph is complete when all artifact levels when traces are calculated between all artifacts in dataset.

"""

import os
from typing import List, Optional

import numpy as np
from igraph import Graph

from api.constants.dataset import (
    TraceId2SimilarityMatrixMap,
)
from api.constants.techniques import ArtifactLevel, N_ITERATIONS_TRACE_PROPAGATION
from api.datasets.builder.dependency_graph_operations import (
    get_all_paths,
    get_paths_to_complete_graph,
)
from api.datasets.builder.graph_path_map import GraphPathMap
from api.datasets.builder.ibuilder import IBuilder
from api.datasets.builder.structure_definition import DatasetStructureDefinition
from api.datasets.builder.trace_id_map import TraceIdMap
from api.datasets.builder.trace_matrix import TraceMatrix
from api.datasets.builder.trace_matrix_map import (
    TraceMatrixMap,
)
from api.technique.definitions.transitive.calculator import (
    perform_transitive_aggregation_on_component_techniques,
)
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.aggregation.technique_aggregation_calculator import (
    aggregate_techniques,
)


class TraceMatrixBuilder(IBuilder):
    """
    The following module is responsible for creating all trace matrices in a dataset. Namely, the following features
    are used to satisfy this task:
    1. Trace links are read using the structure definition of a dataset. Trace matrices are constructed using these
    links. This step is reference
    """

    def __init__(
        self,
        structure_definition: Optional[DatasetStructureDefinition] = None,
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
        self.artifact_levels = []
        if trace_matrix_map is not None:
            self.trace_matrix_map: TraceMatrixMap = trace_matrix_map
        else:
            self.trace_matrix_map: TraceMatrixMap = TraceMatrixMap()

    def set_artifact_levels(self, levels: List[ArtifactLevel]):
        """
        Sets the artifacts whose trace matrices we are constructing
        :param levels:
        :return:
        """
        self.artifact_levels = levels

    def __getitem__(self, item):
        return self.trace_matrix_map[item]

    def build(self):
        """
        For every combination of nodes, computes all possible trace matrices between them and combines them setting
        it as the final trace matrix.
        :return: None
        """
        self.build_matrices_defined_in_dataset()
        self.build_missing_matrices()
        self.iteratively_add_transitive_traces()

    def build_matrices_defined_in_dataset(self):
        """
        For
        :return:
        """
        for trace_id, matrix_path in self.structure_definition[
            DatasetStructureDefinition.TRACES_KEY
        ].items():
            a_level, b_level = trace_id.split("-")
            a_index, b_index = int(a_level), int(b_level)

            if matrix_path is None:
                continue

            trace_matrix = TraceMatrix.create_trace_matrix_from_path(
                self.artifact_levels[a_index]["id"],
                a_index,
                self.artifact_levels[b_index]["id"],
                b_index,
                matrix_path,
            )

            self.trace_matrix_map[trace_id] = trace_matrix

    def build_missing_matrices(self):
        """
        For each trace matrix missing in a trace dependency graph, this constructs a matrix for it using the transitive
        traces already defined in dataset.
        :return: None
        """
        dependency_graph = self.create_trace_matrix_dependency_graph()

        missing_graph_paths: GraphPathMap = get_paths_to_complete_graph(
            self.trace_matrix_map.get_trace_ids(),
            dependency_graph,
            len(self.artifact_levels),
        )
        transitive_matrix_map: TraceMatrixMap = (
            self.create_transitive_trace_matrices_for_paths(missing_graph_paths)
        )
        self.trace_matrix_map.update(transitive_matrix_map)
        for missing_path_id, _ in missing_graph_paths:  #
            a_index, b_index = TraceIdMap.parse_trace_id(missing_path_id)
            dependency_graph.add_edge(a_index, b_index)

    def iteratively_add_transitive_traces(
        self, iterations: int = N_ITERATIONS_TRACE_PROPAGATION
    ):
        """
        For a specified number of iterations, all transitive traces are calculated and added to existing trace matrices.
        :param iterations: How many iterations upon which to calculate and add transitive trace links
        :return: None
        """
        for _ in range(iterations):
            self.add_transitive_traces()

    def add_transitive_traces(self):
        """
        Calculates all transitive traces between all trace matrices and adds them to any matrices missing them.
        Transitive traces are calculated by taking the dot-product (with max aggregator instead of sum) of lists of
        trace matrices corresponding to a path in the dependency graph of between artifacts.
        :return:
        """
        graph = self.create_trace_matrix_dependency_graph()
        direct_path_map: GraphPathMap = GraphPathMap()
        for trace_id in self.trace_matrix_map.get_trace_ids():
            a_index, b_index = TraceIdMap.parse_trace_id(trace_id)
            direct_path_map[trace_id] = get_all_paths(graph, a_index, b_index)
        updated_trace_matrix_map: TraceMatrixMap = (
            self.create_transitive_trace_matrices_for_paths(direct_path_map)
        )
        self.trace_matrix_map.update(updated_trace_matrix_map)

    def export(self, path_to_dataset: str):
        """
        Exports trace built trace matrices to given dataset folder where each matrix file is a .npy file named
        using the matrix's trace id.
        :param path_to_dataset: path to parsed dataset folder
        :return: None
        """
        for trace_id in self.trace_matrix_map.get_trace_ids():
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
        :return: Graph
        """
        return TraceMatrixBuilder.create_dependency_graph_with_trace_ids(
            self.trace_matrix_map.get_trace_ids(), len(self.artifact_levels)
        )

    def create_transitive_trace_matrices_for_paths(
        self,
        graph_paths_map: GraphPathMap,
    ) -> TraceMatrixMap:
        """
        For each set of graph paths in GraphPathMap, a matrix is calculated by taking the dot-produce (with max
        aggregator) all of paths between two artifact levels; then, the element-wise max all matrices is stored.
        :param graph_paths_map: set of graph paths with trace ids (corresponding to end and beginning of the set of
        paths)
        :return: set of matrices where each matrix corresponds to a set of graph paths in GraphPathMap
        """
        path_matrix_map: TraceId2SimilarityMatrixMap = self.calculate_matrix_for_paths(
            graph_paths_map
        )
        result_map = TraceMatrixMap()
        for trace_id, path_matrix in path_matrix_map.items():
            a_index, b_index = TraceIdMap.parse_trace_id(trace_id)
            path_matrix = TraceMatrix(
                a_index,
                self.artifact_levels[a_index]["id"],
                b_index,
                self.artifact_levels[b_index]["id"],
                path_matrix,
            )
            result_map[trace_id] = path_matrix

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
                matrices_to_multiply = self.trace_matrix_map.get_trace_matrices_in_path(
                    transitive_path
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

    @staticmethod
    def create_dependency_graph_with_trace_ids(edges: List[str], n_nodes: int):
        """
        For a given amount of nodes, adds edges defined by trace ids
        :param edges: list of strings in trace id format ([source_node]-[target_node])
        :param n_nodes: how many total nodes exist in graph.
        :return:
        """
        graph = Graph()
        graph.add_vertices(n_nodes)
        for matrix_id in edges:
            a_level, b_level = matrix_id.split("-")
            a_index, b_index = int(a_level), int(b_level)
            graph.add_edge(a_index, b_index)
        return graph
