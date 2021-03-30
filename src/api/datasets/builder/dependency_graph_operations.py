"""
Contains a set of functions operating on trace dependency graphs.
"""
from typing import List, Optional

from igraph import Graph

from api.constants.dataset import GraphPath
from api.datasets.builder.graph_path_map import GraphPathMap
from api.datasets.builder.trace_id_map import TraceIdMap


def get_paths_to_complete_graph(
    trace_ids: List[str], dependency_graph: Graph, n_levels: int
) -> GraphPathMap:
    """
    For every combination of nodes in graph without an edge, all transitive paths between them are calculated and
    returned.
    :param trace_ids: list of trace id representing the trace matrices defined in a dataset
    :param n_levels: how many levels exist in the dataset
    :param dependency_graph: the graph modeling trace dependencies
    :return: set of sets of transitive paths
    """
    missing_paths: GraphPathMap = TraceIdMap[GraphPathMap]()
    for a_index in range(n_levels):
        for b_index in range(n_levels):
            trace_id = "%d-%d" % (a_index, b_index)
            if (
                a_index != b_index
                and not _contains_trace_id(trace_ids, trace_id)
                and trace_id not in missing_paths
            ):
                transitive_paths: List[List[int]] = get_all_paths(
                    dependency_graph, a_index, b_index
                )

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


def _contains_trace_id(
    traces: List[str],
    trace_id: str,
):
    """
    TODO
    :param traces:
    :param trace_id:
    :return:
    """
    index = _id_exists_in_traces(traces, trace_id)
    return index != 0


def _id_exists_in_traces(
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
    id_r = TraceIdMap.reverse_id(trace_id)
    if id_r in traces:
        return -1
    return 0
