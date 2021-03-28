import numpy as np
from igraph import Graph

from api.datasets.builder.dataset_builder import DatasetBuilder
from api.datasets.builder.trace_matrix_creator import (
    TraceMatrixCreator,
    contains_trace_id,
    create_similarity_matrix_map_for_graph_paths,
    create_trace_matrix_graph,
    create_trace_matrix_map,
    get_graph_paths_map_to_missing_paths,
)
from api.datasets.trace_matrix import TraceMatrix
from tests.res.smart_test import SmartTest


class TestTransitiveTraceMatrixCreator(SmartTest):
    def test_create_transitive_trace_matrices_with_fake_dataset(self):
        dataset_builder = DatasetBuilder("MockDataset")
        dataset_builder.create_levels()

        # erase trace matrix
        dataset_builder.structure_file["traces"]["0-2"] = None
        dataset_builder.defined_trace_matrices.remove("0-2")
        new_trace_map, graph = create_trace_matrix_map(
            dataset_builder.structure_file, dataset_builder.levels
        )

        self.assertEqual(3, len(new_trace_map.trace_matrix_map.keys()))
        self.assertIsNotNone(new_trace_map.trace_matrix_map["0-2"])
        self.assertIsNotNone(new_trace_map.trace_matrix_map["0-2"].matrix)
        self.assertEqual(1, new_trace_map.trace_matrix_map["0-2"].matrix[0, 0])
        self.assertEqual(
            2, new_trace_map.trace_matrix_map["0-2"].matrix.sum(axis=1).sum()
        )

        self.assertEqual(3, len(graph.es))

    def test_create_transitive_trace_matrices_with_warc(self):
        dataset_builder = DatasetBuilder("SAMPLE_WARC")
        dataset_builder.create_levels()

        # erase trace matrix
        new_trace_map, graph = create_trace_matrix_map(
            dataset_builder.structure_file, dataset_builder.levels
        )

        self.assertIsNotNone(new_trace_map.trace_matrix_map["1-2"])
        self.assertEqual(3, len(graph.es))

    """
    create_similarity_matrix_map_for_graph_paths
    """
    req2design = TraceMatrix(None, None, None, None, matrix=np.array([[1]]))
    design2code = TraceMatrix(None, None, None, None, matrix=np.array([[0, 0, 1]]))
    reqs2code = TraceMatrix(None, None, None, None, matrix=np.array([[1, 0, 0]]))
    reqs2tasks = TraceMatrix(None, None, None, None, matrix=np.array([[1]]))
    tasks2code = TraceMatrix(None, None, None, None, matrix=np.array([[0, 1, 0]]))

    trace_matrix_map = {
        "0-1": req2design,
        "1-2": design2code,
        "0-2": reqs2code,
        "0-3": tasks2code,
        "3-2": tasks2code,
    }

    def test_create_similarity_matrix_map_for_graph_paths_with_four_levels(self):
        graph_paths = {"0-2": [[0, 2], [0, 1, 2], [0, 3, 2]]}
        similarity_matrix_map = create_similarity_matrix_map_for_graph_paths(
            graph_paths, self.trace_matrix_map
        )
        values = similarity_matrix_map["0-2"]
        self.assertEqual(1, values[0, 0])
        self.assertEqual(1, values[0, 1])
        self.assertEqual(1, values[0, 2])
        self.assertEqual(0, self.reqs2code.matrix[0, 2])

    def test_create_trace_matrix_graph(self):
        graph: Graph = create_trace_matrix_graph(["0-1", "1-2"], 3)
        self.assertFalse(graph.are_connected(0, 2))
        self.assertTrue(graph.are_connected(0, 1))
        self.assertTrue(graph.are_connected(1, 2))
        self.assertEqual(3, len(graph.vs))

        path = graph.get_shortest_paths(0, 2)
        self.assertEqual(1, len(path))
        self.assertEqual([0, 1, 2], path[0])

    def test_create_trace_matrix_graph_with_backwards_search(self):
        graph: Graph = create_trace_matrix_graph(["0-1", "0-2"], 3)
        path = graph.get_shortest_paths(1, 2)
        self.assertEqual(1, len(path))
        self.assertEqual([1, 0, 2], path[0])

    def test_create_trace_matrices_in_definition(self):
        dataset_builder = DatasetBuilder("MockDataset")
        dataset_builder.structure_file["traces"]["0-2"] = None
        dataset_builder.create_levels()

        trace_matrix_map = TraceMatrixCreator(
            dataset_builder.structure_file, dataset_builder.levels
        )

        self.assertEqual(2, len(trace_matrix_map.trace_matrix_map.keys()))
        self.assertTrue("0-1" in trace_matrix_map.trace_matrix_map.keys())
        self.assertTrue("1-2" in trace_matrix_map.trace_matrix_map.keys())
        self.assertFalse("0-2" in trace_matrix_map.trace_matrix_map.keys())

        self.assertEqual(
            0, trace_matrix_map.trace_matrix_map["0-1"].top_index
        )  # TODO: Implement lookup
        self.assertEqual(1, trace_matrix_map.trace_matrix_map["0-1"].bottom_index)

    def test_normalize_original_matrices(self):
        db = DatasetBuilder("MockDataset")
        db.create_levels()
        trace_matrix_map, graph = create_trace_matrix_map(db.structure_file, db.levels)

        self.assertEqual(1, trace_matrix_map.trace_matrix_map["0-2"].matrix[0][2])

    def test_get_trace_path_map_to_missing_links(self):
        traces = ["1-4", "4-0", "0-2", "2-3"]
        graph = create_trace_matrix_graph(traces, 5)
        missing_paths = get_graph_paths_map_to_missing_paths(traces, graph, 5)
        self.assertEqual(6, len(missing_paths))
        self.assertTrue("0-1" in missing_paths)
        self.assertTrue("1-2" in missing_paths)
        self.assertTrue("1-3" in missing_paths)
        self.assertTrue("3-4" in missing_paths)
        self.assertTrue("2-4" in missing_paths)
        self.assertTrue("0-3" in missing_paths)

    def test_get_paths_to_missing_traces_with_fakedataset(self):
        dataset_builder = DatasetBuilder("MockDataset")
        dataset_builder.create_levels()
        dataset_builder.defined_trace_matrices.remove("0-2")
        graph = create_trace_matrix_graph(dataset_builder.defined_trace_matrices, 3)

        paths = get_graph_paths_map_to_missing_paths(
            dataset_builder.defined_trace_matrices, graph, 3
        )

        self.assertEqual(1, len(paths.keys()))
        self.assertEqual(1, len(paths["0-2"]))
        self.assertEqual([0, 1, 2], paths["0-2"][0])

    def test_get_paths_to_missing_traces_with_warc(self):
        """
        Checks that the missing trace matrix in WARC is covered using a transitive path using the
        defined trace matrices.
        :return: None
        """
        dataset_builder = DatasetBuilder("SAMPLE_WARC")
        dataset_builder.create_levels()
        graph = create_trace_matrix_graph(dataset_builder.defined_trace_matrices, 3)
        paths = get_graph_paths_map_to_missing_paths(
            dataset_builder.defined_trace_matrices, graph, 3
        )
        self.assertEqual(1, len(paths.keys()))
        self.assertEqual(1, len(paths["0-1"]))
        self.assertEqual([0, 2, 1], paths["0-1"][0])

    def test_contains_id(self):
        self.assertTrue(contains_trace_id(["0-1"], "0-1"))
        self.assertTrue(contains_trace_id(["0-1"], "1-0"))
        self.assertFalse(contains_trace_id(["0-1"], "0-2"))
