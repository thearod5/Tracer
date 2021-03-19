from typing import List, Dict

from igraph import Graph

from api.constants.techniques import N_ITERATIONS_TRACE_PROPAGATION
from api.datasets.builder.trace_creator import create_trace_matrix_from_path
from api.datasets.multi_level_artifacts import ArtifactLevel
from api.datasets.trace_matrix import TraceMatrix
from api.technique.definitions.transitive.calculator import \
    perform_transitive_aggregation_on_component_techniques
from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod
from api.technique.variationpoints.aggregation.technique_aggregation_calculator import aggregate_techniques
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix

"""
A Trace Matrix map contains as keys TraceIds and as values a TraceMatrix

A TraceId is a string in the form of [artifact_a_index]-[artifact_b_index]
"""
TraceId2SimilarityMatrixMap = Dict[
    str, SimilarityMatrix]  # mapping between trace id and its corresponding SimilarityMatrix as traces
TraceId2TraceMatrixMap = Dict[str, TraceMatrix]  # for retrieving TraceMatrix values at east
GraphPath = List[int]  # ordered list of vertices representing a pat

"""
A TracePathMap is a dict mapping from TraceIds to a list of integers representing
the nodes indices for a certain path
"""
TraceId2GraphPathsMap = Dict[str, List[GraphPath]]


def create_trace_matrix_map(structure_file: dict,
                            levels: [ArtifactLevel]) -> (TraceId2TraceMatrixMap, Graph):
    """
    For every combination of nodes verifies or creates path between
    each node to create a complete graph.
    :param structure_file: a dataset's structure definition
    :param levels: parsed ArtifactLevels with indices corresponding to level index
    :return: map with all trace technique_matrices defined
       """
    n_levels = len(levels)
    direct_trace_matrix_map = create_trace_id_2_trace_matrix_map_from_definition(structure_file, levels)
    direct_trace_ids = direct_trace_matrix_map.keys()

    # create dependency graph
    dependency_graph = create_trace_matrix_graph(direct_trace_ids, n_levels)

    # for each undefined path for nodes a and b find all graph_paths between a and b
    missing_graph_path = get_graph_paths_map_to_missing_paths(direct_trace_ids,
                                                              dependency_graph,
                                                              n_levels)
    transitive_matrix_map = create_trace_matrix_map_from_graph_path_map(missing_graph_path,
                                                                        direct_trace_matrix_map,
                                                                        levels)
    for path_id in missing_graph_path.keys():  #
        a_index, b_index = parse_trace_id(path_id)
        dependency_graph.add_edge(a_index, b_index)

    direct_trace_matrix_map.update(transitive_matrix_map)

    # update original graph_paths with transitive ones
    for i in range(
            N_ITERATIONS_TRACE_PROPAGATION):  # information prorogation takes some iterations to stabilize, found 5 to be sufficient.
        direct_trace_matrix_map = normalize_original_matrices(structure_file,
                                                              direct_trace_matrix_map,
                                                              dependency_graph,
                                                              levels)
    return direct_trace_matrix_map, dependency_graph


def create_trace_matrix_map_from_graph_path_map(graph_paths_map: TraceId2GraphPathsMap,
                                                trace_matrix_map: TraceId2TraceMatrixMap,
                                                levels: [ArtifactLevel]) -> TraceId2TraceMatrixMap:
    """

    :param trace_matrix_map:
    :param graph_paths_map:
    :param levels:
    :return:
    """
    transitive_trace_matrix_map: TraceId2SimilarityMatrixMap = create_similarity_matrix_map_for_graph_paths(
        graph_paths_map,
        trace_matrix_map)
    result_map = {}
    for trace_id, similarity_matrix in transitive_trace_matrix_map.items():
        a_index, b_index = parse_trace_id(trace_id)
        result_map[trace_id] = TraceMatrix(a_index, levels[a_index]["id"],
                                           b_index, levels[b_index]["id"],
                                           similarity_matrix)

    return result_map


def create_similarity_matrix_map_for_graph_paths(graph_paths: TraceId2GraphPathsMap,
                                                 trace_matrix_map: TraceId2TraceMatrixMap) -> TraceId2SimilarityMatrixMap:
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
            matrices_to_multiply = get_transitive_matrices_in_path(trace_matrix_map, transitive_path)
            transitive_similarity_matrix = perform_transitive_aggregation_on_component_techniques(
                matrices_to_multiply,
                transitive_aggregation)
            transitive_similarity_matrices.append(transitive_similarity_matrix)
        aggregated_matrix = aggregate_techniques(transitive_similarity_matrices,
                                                 transitive_aggregation)
        result_matrices[transitive_path_key] = aggregated_matrix
    return result_matrices


def create_trace_matrix_graph(trace_matrix_keys: [str], n_levels: int) -> Graph:
    """
    Creates a dependency graph between artifacts layers using trace technique_matrices as edges
    :param n_levels: The number of artifact levels in the dataset, used to define the number of nodes
    :param trace_matrix_keys: list of strings in format [source_index]-[target_index] representing edges in graph.
    :return: Graph - Represents the vertices and edges defined by the given traces
    """
    g = Graph()
    g.add_vertices(n_levels)
    for matrix_id in trace_matrix_keys:
        a_level, b_level = matrix_id.split("-")
        a_index, b_index = int(a_level), int(b_level)
        g.add_edge(a_index, b_index)
    return g


def normalize_original_matrices(structure_file: dict,
                                trace_matrix_map: TraceId2TraceMatrixMap,
                                graph: Graph,
                                levels: [ArtifactLevel]) -> TraceId2TraceMatrixMap:
    """
    returns the trace matrix with all transitive and direct graph_paths.
    :param structure_file:
    :param trace_matrix_map: a TraceMatrixMap containing all transitive and direct traces
    :param graph: The dependency graph of each trace matrix
    :param levels:
    :return:
    """
    direct_path_map = {}
    for trace_id in trace_matrix_map.keys():
        a_index, b_index = parse_trace_id(trace_id)
        direct_path_map[trace_id] = find_all_paths(graph, a_index, b_index)
    updated_trace_matrix_map = create_trace_matrix_map_from_graph_path_map(direct_path_map,
                                                                           trace_matrix_map,
                                                                           levels)
    trace_matrix_map.update(updated_trace_matrix_map)
    return trace_matrix_map


def get_graph_paths_map_to_missing_paths(trace_ids: [str],
                                         dependency_graph: Graph,
                                         n_levels: int) -> TraceId2GraphPathsMap:
    """
    For every combination of nodes verifies or creates path between
    each node to create a complete graph.
    :param trace_ids: list of trace id representing the trace technique_matrices defined in a dataset
    :param n_levels: how many levels exist in the dataset
    :param dependency_graph: the graph modeling trace dependancies
    :return:
    """
    missing_paths = {}
    for a_index in range(n_levels):
        for b_index in range(n_levels):
            trace_id = "%d-%d" % (a_index, b_index)
            if a_index != b_index and \
                    not contains_trace_id(trace_ids, trace_id) and \
                    not contains_trace_id(missing_paths, trace_id):
                transitive_paths = find_all_paths(dependency_graph, a_index, b_index)

                if len(transitive_paths) == 0:
                    raise Exception("there is no path to generate traces for levels %s" % trace_id)
                missing_paths[trace_id] = transitive_paths
    return missing_paths


def get_transitive_matrices_in_path(trace_matrix_map: TraceId2TraceMatrixMap, transitive_path: GraphPath) -> [
    SimilarityMatrix]:
    matrices_to_multiple = []
    for node_index in range(len(transitive_path) - 1):
        left_node_index = transitive_path[node_index]
        right_node_index = transitive_path[node_index + 1]
        trace_id = "%d-%d" % (left_node_index, right_node_index)
        next_similarity_matrix = get_similarity_matrix_in_trace_matrix_map(trace_matrix_map, trace_id)
        matrices_to_multiple.append(next_similarity_matrix)
    return matrices_to_multiple


def create_trace_id_2_trace_matrix_map_from_definition(structure_file: dict,
                                                       levels: [ArtifactLevel]) -> TraceId2TraceMatrixMap:
    """
    For each non-empty path_to_trace_matrix in structure file,
    create a TraceMatrix and store in dict with [level_index]-[other_level_index]
    as key.
    :return: dict
    """
    trace_matrices = {}
    for trace_id, matrix_path in structure_file["traces"].items():
        a_level, b_level = trace_id.split("-")
        a_index, b_index = int(a_level), int(b_level)
        if matrix_path is None:
            continue
        trace_matrices[trace_id] = create_trace_matrix_from_path(levels[a_index]["id"],
                                                                 a_index,
                                                                 levels[b_index]["id"],
                                                                 b_index,
                                                                 matrix_path)
    return trace_matrices


def get_similarity_matrix_in_trace_matrix_map(trace_matrix_map: TraceId2TraceMatrixMap,
                                              trace_id: str) -> SimilarityMatrix:
    index = id_exists_in_traces(trace_matrix_map.keys(), trace_id)
    if index == 1:
        return trace_matrix_map[trace_id].matrix
    if index == -1:
        return trace_matrix_map[reverse_id(trace_id)].matrix.T


def contains_trace_id(traces: [str], trace_id: str, ):
    index = id_exists_in_traces(traces, trace_id)
    return index != 0


def id_exists_in_traces(traces: [str], trace_id: str, ):
    if trace_id in traces:
        return 1
    id_r = reverse_id(trace_id)
    if id_r in traces:
        return -1
    return 0


def reverse_id(trace_id: str):
    a, b = trace_id.split("-")
    return "%s-%s" % (b, a)


def parse_trace_id(trace_id: str):
    a, b = trace_id.split("-")
    return int(a), int(b)


# Retrieved from: https://stackoverflow.com/questions/29320556/finding-longest-path-in-a-graph
def find_all_paths(graph, start, end, mode='OUT', maxlen=None) -> [GraphPath]:
    def find_all_paths_aux(adjlist, start, end, path, maxlen=None):
        path = path + [start]
        if start == end:
            return [path]
        paths = []
        if maxlen is None or len(path) <= maxlen:
            for node in adjlist[start] - set(path):
                paths.extend(find_all_paths_aux(adjlist, node, end, path, maxlen))
        return paths

    adj_list = [set(graph.neighbors(node, mode=mode)) \
                for node in range(graph.vcount())]
    all_paths = []
    start = start if type(start) is list else [start]
    end = end if type(end) is list else [end]
    for s in start:
        for e in end:
            all_paths.extend(find_all_paths_aux(adj_list, s, e, [], maxlen))
    return all_paths
