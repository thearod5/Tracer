"""
The following module creates a module responsible for parsing trace matrices using the paths definition
in structure definitions.
"""

from api.constants.dataset import (
    GraphPath,
    SimilarityMatrix,
    TraceId2GraphPathsMap,
    TraceId2SimilarityMatrixMap,
)
from api.datasets.builder.trace_parser import parse_trace_id, reverse_id
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
TODO

A Trace Matrix map contains as keys TraceIds and as values a TraceMatrix
A TraceId is a string in the form of [artifact_a_index]-[artifact_b_index]

A TracePathMap is a dict mapping from TraceIds to a list of integers representing
the nodes indices for a certain path
"""
from typing import List, Optional

from igraph import Graph

from api.constants.techniques import ArtifactLevel, N_ITERATIONS_TRACE_PROPAGATION

from api.datasets.trace_matrix import TraceId2TraceMatrixMap, TraceMatrix


class TraceMatrixCreator:
    """
    The following module is responsible for creating all trace matrices in a dataset.
    """

    def __init__(self, structure_file: dict, levels: List[ArtifactLevel]):
        """
        For each non-empty path_to_trace_matrix in structure file,
        create a TraceMatrix and store in dict with [source_level_index]-[target_level_index]
        as key.
        :param structure_file: json file containing defining the paths to artifacts and trace matrices
        :param levels: parsed artifacts level corresponding to levels in structure file
        :return: TODO
        """
        trace_matrices = {}
        for trace_id, matrix_path in structure_file["traces"].items():
            a_level, b_level = trace_id.split("-")
            a_index, b_index = int(a_level), int(b_level)
            if matrix_path is None:
                continue
            trace_matrix = TraceMatrix.create_trace_matrix_from_path(
                levels[a_index]["id"],
                a_index,
                levels[b_index]["id"],
                b_index,
                matrix_path,
            )

            if a_index < b_index:
                trace_matrices[trace_id] = trace_matrix
            else:
                r_trace_id = "%d-%d" % (b_index, a_index)
                trace_matrices[r_trace_id] = trace_matrix.transpose()
        self.trace_matrix_map: TraceId2TraceMatrixMap = trace_matrices
        self.levels = levels

    def normalize_original_matrices(self):
        """
        returns the trace matrix with all transitive and direct graph_paths.
        :param graph: The dependency graph of each trace matrix
        :return:
        """
        graph = self.create_dependency_graph()
        direct_path_map = {}
        for trace_id in self.trace_matrix_map.keys():
            a_index, b_index = parse_trace_id(trace_id)
            direct_path_map[trace_id] = get_all_paths(graph, a_index, b_index)
        updated_trace_matrix_map = create_trace_matrix_map_from_graph_path_map(
            direct_path_map, self.trace_matrix_map, self.levels
        )
        self.trace_matrix_map.update(updated_trace_matrix_map)

    def create_dependency_graph(self):
        n_levels = len(self.levels)
        direct_trace_ids: List[str] = list(map(to_string, self.trace_matrix_map.keys()))
        graph = create_trace_matrix_graph(direct_trace_ids, n_levels)
        return graph

    def create_trace_matrix_map(self):
        """
        For every combination of nodes verifies that path already exists or creates path between them to form a
        a complete graph.
        TODO: RENAME TO CREATE_DEPENDENY_GRAPH
        :return: map with all trace technique_matrices defined
        """
        n_levels = len(self.levels)
        direct_trace_ids: List[str] = list(map(to_string, self.trace_matrix_map.keys()))

        # create dependency graph
        dependency_graph = self.create_dependency_graph()

        # for each undefined path for nodes a and b find all graph_paths between a and b
        missing_graph_path = get_graph_paths_map_to_missing_paths(
            direct_trace_ids, dependency_graph, n_levels
        )
        transitive_matrix_map = create_trace_matrix_map_from_graph_path_map(
            missing_graph_path, self.trace_matrix_map, self.levels
        )
        for path_id in missing_graph_path:  #
            a_index, b_index = parse_trace_id(path_id)
            dependency_graph.add_edge(a_index, b_index)

        self.trace_matrix_map.update(transitive_matrix_map)

        # update original graph_paths with transitive ones
        for _ in range(N_ITERATIONS_TRACE_PROPAGATION):
            self.normalize_original_matrices()
        return dependency_graph


def create_trace_matrix_map_from_graph_path_map(
    graph_paths_map: TraceId2GraphPathsMap,
    trace_matrix_map: TraceId2TraceMatrixMap,
    levels: List[ArtifactLevel],
) -> TraceId2TraceMatrixMap:
    """
    TODO
    :param trace_matrix_map:
    :param graph_paths_map:
    :param levels:
    :return:
    """
    transitive_trace_matrix_map: TraceId2SimilarityMatrixMap = (
        create_similarity_matrix_map_for_graph_paths(graph_paths_map, trace_matrix_map)
    )
    result_map = {}
    for trace_id, similarity_matrix in transitive_trace_matrix_map.items():
        a_index, b_index = parse_trace_id(trace_id)
        result_map[trace_id] = TraceMatrix(
            a_index,
            levels[a_index]["id"],
            b_index,
            levels[b_index]["id"],
            similarity_matrix,
        )

    return result_map


def create_similarity_matrix_map_for_graph_paths(
    graph_paths: TraceId2GraphPathsMap, trace_matrix_map: TraceId2TraceMatrixMap
) -> TraceId2SimilarityMatrixMap:
    """
    For each key corresponding to a TraceId a similarity matrix is calculated for each assigned path.
    For all similarity technique_matrices the element-wise max is take to construct the final matrix
    :param graph_paths: TraceIds as keys and list of GraphPaths as values
    :param trace_matrix_map: TraceIds as keys and TraceMatrix as values
    :return: dict with TraceIds as keys and SimilarityMatrices as values
    """
    transitive_aggregation = AggregationMethod.MAX
    result_matrices = {}
    for transitive_path_key, transitive_paths in graph_paths.items():
        transitive_similarity_matrices = []
        for transitive_path in transitive_paths:
            matrices_to_multiply = get_transitive_matrices_in_path(
                trace_matrix_map, transitive_path
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


def create_trace_matrix_graph(trace_matrix_keys: List[str], n_levels: int) -> Graph:
    """
    Creates a dependency graph between artifacts layers where an edge exists between layers if there is a
    trace id (e.g. [source_index]-[target_index]) in trace_matrix_keys
    :param trace_matrix_keys: list of strings in format [source_index]-[target_index] representing edges in graph.
    :param n_levels: The number of artifact levels in the dataset, used to define the number of nodes
    :return: Graph - Represents the vertices and edges defined by the given traces
    """
    graph = Graph()
    graph.add_vertices(n_levels)
    for matrix_id in trace_matrix_keys:
        a_level, b_level = matrix_id.split("-")
        a_index, b_index = int(a_level), int(b_level)
        graph.add_edge(a_index, b_index)
    return graph


def get_transitive_matrices_in_path(
    trace_matrix_map: TraceId2TraceMatrixMap, transitive_path: GraphPath
) -> List[SimilarityMatrix]:
    """
    TODO
    :param trace_matrix_map:
    :param transitive_path:
    :return:
    """
    matrices_to_multiple = []
    for node_index in range(len(transitive_path) - 1):
        left_node_index = transitive_path[node_index]
        right_node_index = transitive_path[node_index + 1]
        trace_id = "%d-%d" % (left_node_index, right_node_index)
        next_similarity_matrix = get_similarity_matrix_in_trace_matrix_map(
            trace_matrix_map, trace_id
        )
        matrices_to_multiple.append(next_similarity_matrix)
    return matrices_to_multiple


def get_similarity_matrix_in_trace_matrix_map(
    trace_matrix_map: TraceId2TraceMatrixMap, trace_id: str
) -> SimilarityMatrix:
    """
    TODO
    :param trace_matrix_map:
    :param trace_id:
    :return:
    """
    index = id_exists_in_traces(list(trace_matrix_map.keys()), trace_id)
    if index == 1:
        return trace_matrix_map[trace_id].matrix
    if index == -1:
        return trace_matrix_map[reverse_id(trace_id)].matrix.T
    raise Exception("Reached end of statement, id might not exist in trace matrix map")


def contains_trace_id(
    traces: List[str],
    trace_id: str,
):
    """
    TODO
    :param traces:
    :param trace_id:
    :return:
    """
    index = id_exists_in_traces(traces, trace_id)
    return index != 0


def id_exists_in_traces(
    traces: List[str],
    trace_id: str,
):
    """
    TODO
    :param traces:
    :param trace_id:
    :return:
    """
    if trace_id in traces:
        return 1
    id_r = reverse_id(trace_id)
    if id_r in traces:
        return -1
    return 0


def get_graph_paths_map_to_missing_paths(
    trace_ids: List[str], dependency_graph: Graph, n_levels: int
) -> TraceId2GraphPathsMap:
    """
    For every combination of nodes in graph, if no direct link exists between them then one is calculated using
    the transitive paths between the defined edges in the graph.
    :param trace_ids: list of trace id representing the trace matrices defined in a dataset
    :param n_levels: how many levels exist in the dataset
    :param dependency_graph: the graph modeling trace dependencies
    :return: TODO
    """
    missing_paths: TraceId2GraphPathsMap = {}
    for a_index in range(n_levels):
        for b_index in range(n_levels):
            trace_id = "%d-%d" % (a_index, b_index)
            if (
                a_index != b_index
                and not contains_trace_id(trace_ids, trace_id)
                and not contains_trace_id(list(missing_paths.keys()), trace_id)
            ):
                transitive_paths = get_all_paths(dependency_graph, a_index, b_index)

                if len(transitive_paths) == 0:
                    raise Exception(
                        "there is no path to generate traces for levels %s" % trace_id
                    )
                missing_paths[trace_id] = transitive_paths
    return missing_paths


def get_all_paths(
    trace_matrix_dependency_graph: Graph,
    start_index: int,
    end_index: int,
) -> List[GraphPath]:
    """
    Returns list of all possible paths through graph starting and ending at given indices

    Retrieved from: https://stackoverflow.com/questions/29320556/finding-longest-path-in-a-graph
    is defined between them
     :param trace_matrix_dependency_graph: the graph with nodes are artifacts levels with edges if a trace matrix
    :param start_index: int - index of artifact level to start path at
    :param end_index: int - index of artifact lvel to end path at
    :return:
    """
    mode = "OUT"
    max_length: Optional[int] = None

    def find_all_paths_aux(
        adj_list: List[set], start_aux: int, end_aux: int, path, maxlen: int = None
    ):
        path = path + [start_aux]
        if start_aux == end_aux:
            return [path]
        paths = []
        if maxlen is None or len(path) <= maxlen:
            for node in adj_list[start_aux] - set(path):
                paths.extend(find_all_paths_aux(adj_list, node, end_aux, path, maxlen))
        return paths

    adj_list: List[set] = [
        set(trace_matrix_dependency_graph.neighbors(node, mode=mode))
        for node in range(trace_matrix_dependency_graph.vcount())
    ]
    all_paths = []
    start_index = start_index if isinstance(start_index, list) else [start_index]
    end_index = end_index if isinstance(end_index, list) else [end_index]
    for start_path in start_index:
        for end_path in end_index:
            all_paths.extend(
                find_all_paths_aux(adj_list, start_path, end_path, [], max_length)
            )
    return all_paths
