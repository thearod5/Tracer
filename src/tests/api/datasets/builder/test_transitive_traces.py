from typing import List

import numpy as np
import pandas as pd
from igraph import Graph

from api.constants.techniques import ArtifactLevel
from api.datasets.builder.dataset_builder import DatasetBuilder
from api.datasets.builder.graph_operations import (
    contains_trace_id,
    get_paths_to_complete_graph,
)
from api.datasets.builder.graph_path_map import GraphPathMap
from api.datasets.builder.structure_definition import DatasetStructure
from api.datasets.builder.trace_matrix import TraceMatrix
from api.datasets.builder.trace_matrix_builder import (
    TraceMatrixBuilder,
)
from api.datasets.builder.trace_matrix_map import TraceMatrixMap
from api.extension.type_checks import to_string
from tests.res.smart_test import SmartTest


class TestTransitiveTraceMatrixCreator(SmartTest):
    def test_creating_missing_matrices(self):
        """
        For MockDataset, removes trace matrix 0-2 from structure definition and checks that builder is able to
        construct one using transitive traces from the other matrices.
        :return:
        """
        dataset_builder = DatasetBuilder("MockDataset")
        dataset_builder.structure_definition["traces"]["0-2"] = None
        dataset_builder.build()

        trace_matrix_builder = dataset_builder.trace_matrix_builder
        graph = trace_matrix_builder.create_trace_matrix_dependency_graph()

        self.assertEqual(3, len(trace_matrix_builder.trace_matrix_map.get_keys()))
        self.assertIsNotNone(trace_matrix_builder.trace_matrix_map["0-2"])
        self.assertIsNotNone(trace_matrix_builder.trace_matrix_map["0-2"].matrix)
        self.assertEqual(1, trace_matrix_builder.trace_matrix_map["0-2"].matrix[0, 0])
        self.assertEqual(
            2, trace_matrix_builder.trace_matrix_map["0-2"].matrix.sum(axis=1).sum()
        )

        self.assertEqual(3, len(graph.es))

    def test_create_transitive_trace_matrices_with_warc(self):
        dataset_builder = DatasetBuilder("SAMPLE_WARC")
        dataset_builder.build()
        trace_matrix_creator = dataset_builder.trace_matrix_builder
        graph = (
            dataset_builder.trace_matrix_builder.create_trace_matrix_dependency_graph()
        )
        self.assertIsNotNone(trace_matrix_creator.trace_matrix_map["1-2"])
        self.assertEqual(3, len(graph.es))

    """
    create_similarity_matrix_map_for_graph_paths
    """
    level_1 = pd.DataFrame([{"id": "R1", "body": ""}])
    level_2 = pd.DataFrame([{"id": "D1", "body": ""}])
    level_3 = pd.DataFrame(
        [
            {"id": "C1", "body": ""},
            {"id": "C2", "body": ""},
            {"id": "C3", "body": ""},
        ]
    )

    level_4 = pd.DataFrame([{"id": "T1", "body": ""}])
    artifacts: List[ArtifactLevel] = [level_1, level_2, level_3, level_4]

    req2design = TraceMatrix(None, None, None, None, matrix=np.array([[1]]))
    design2code = TraceMatrix(None, None, None, None, matrix=np.array([[0, 0, 1]]))
    reqs2code = TraceMatrix(None, None, None, None, matrix=np.array([[1, 0, 0]]))
    reqs2tasks = TraceMatrix(None, None, None, None, matrix=np.array([[1]]))
    tasks2code = TraceMatrix(None, None, None, None, matrix=np.array([[0, 1, 0]]))

    trace_matrix_map = TraceMatrixMap()
    trace_matrix_map["0-1"] = req2design
    trace_matrix_map["1-2"] = design2code
    trace_matrix_map["0-2"] = reqs2code
    trace_matrix_map["0-3"] = tasks2code
    trace_matrix_map["3-2"] = tasks2code

    structure_definition_json = {
        DatasetStructure.ARTIFACT_KEY: {"0": "", "1": "", "2": "", "3": ""},
        DatasetStructure.TRACES_KEY: trace_matrix_map,
    }

    def test_create_similarity_matrix_map_for_graph_paths_with_four_levels(self):
        trace_matrix_creator = TraceMatrixBuilder(
            trace_matrix_map=self.trace_matrix_map
        )
        trace_matrix_creator.set_levels(self.artifacts)
        graph_paths = GraphPathMap()
        graph_paths["0-2"] = [[0, 2], [0, 1, 2], [0, 3, 2]]
        similarity_matrix_map = trace_matrix_creator.calculate_matrix_for_paths(
            graph_paths
        )
        values = similarity_matrix_map["0-2"]
        self.assertEqual(1, values[0, 0])
        self.assertEqual(1, values[0, 1])
        self.assertEqual(1, values[0, 2])
        self.assertEqual(0, self.reqs2code.matrix[0, 2])

    def test_create_trace_matrix_graph(self):
        graph: Graph = TraceMatrixBuilder.create_dependency_graph(["0-1", "1-2"], 3)
        self.assertFalse(graph.are_connected(0, 2))
        self.assertTrue(graph.are_connected(0, 1))
        self.assertTrue(graph.are_connected(1, 2))
        self.assertEqual(3, len(graph.vs))

        path = graph.get_shortest_paths(0, 2)
        self.assertEqual(1, len(path))
        self.assertEqual([0, 1, 2], path[0])

    def test_create_trace_matrix_graph_with_backwards_search(self):
        graph: Graph = TraceMatrixBuilder.create_dependency_graph(["0-1", "0-2"], 3)
        path = graph.get_shortest_paths(1, 2)
        self.assertEqual(1, len(path))
        self.assertEqual([1, 0, 2], path[0])

    def test_create_trace_matrices_in_definition(self):
        dataset_builder = DatasetBuilder("MockDataset")
        dataset_builder.structure_definition["traces"]["0-2"] = None
        dataset_builder.artifact_builder.build()
        dataset_builder.trace_matrix_builder.set_levels(
            dataset_builder.artifact_builder.artifacts
        )
        dataset_builder.trace_matrix_builder.build_original_trace_matrices()

        trace_matrix_map_keys = (
            dataset_builder.trace_matrix_builder.trace_matrix_map.get_keys()
        )
        self.assertEqual(2, len(trace_matrix_map_keys))
        self.assertIn("0-1", trace_matrix_map_keys)
        self.assertIn("1-2", trace_matrix_map_keys)
        self.assertNotIn("0-2", trace_matrix_map_keys)

        self.assertEqual(0, dataset_builder.trace_matrix_builder["0-1"].top_index)
        self.assertEqual(1, dataset_builder.trace_matrix_builder["0-1"].bottom_index)

    def test_normalize_original_matrices(self):
        db = DatasetBuilder("MockDataset")
        db.build()
        self.assertEqual(1, db.trace_matrix_builder["0-2"].matrix[0][2])

    def test_get_trace_path_map_to_missing_links(self):
        traces = ["1-4", "4-0", "0-2", "2-3"]
        graph = TraceMatrixBuilder.create_dependency_graph(traces, 5)
        missing_paths = get_paths_to_complete_graph(traces, graph, 5)
        self.assertEqual(6, len(missing_paths.get_keys()))
        self.assertTrue("0-1" in missing_paths)
        self.assertTrue("1-2" in missing_paths)
        self.assertTrue("1-3" in missing_paths)
        self.assertTrue("3-4" in missing_paths)
        self.assertTrue("2-4" in missing_paths)
        self.assertTrue("0-3" in missing_paths)

    def test_get_paths_to_missing_traces_with_fakedataset(self):
        dataset_builder = DatasetBuilder("MockDataset")
        dataset_builder.structure_definition["traces"]["0-2"] = None
        dataset_builder.artifact_builder.build()
        dataset_builder.trace_matrix_builder.set_levels(
            dataset_builder.artifact_builder.artifacts
        )
        dataset_builder.trace_matrix_builder.build_original_trace_matrices()
        trace_matrix_map = dataset_builder.trace_matrix_builder.trace_matrix_map
        # TODO: clean up levels dependency

        trace_dependency_graph = (
            dataset_builder.trace_matrix_builder.create_trace_matrix_dependency_graph()
        )
        trace_ids: List[str] = trace_matrix_map.get_keys()
        paths = get_paths_to_complete_graph(trace_ids, trace_dependency_graph, 3)

        self.assertEqual(1, len(paths.get_keys()))
        self.assertEqual(1, len(paths["0-2"]))
        self.assertEqual([0, 1, 2], paths["0-2"][0])

    def test_get_paths_to_missing_traces_with_warc(self):
        """
        Checks that the missing trace matrix in WARC is covered using a transitive path using the
        defined trace matrices.
        :return: None
        """
        dataset_builder = DatasetBuilder("SAMPLE_WARC")
        dataset_builder.artifact_builder.build()
        dataset_builder.trace_matrix_builder.set_levels(
            dataset_builder.artifact_builder.artifacts
        )
        dataset_builder.trace_matrix_builder.build_original_trace_matrices()
        graph = (
            dataset_builder.trace_matrix_builder.create_trace_matrix_dependency_graph()
        )
        trace_ids: List[str] = list(
            map(
                to_string,
                dataset_builder.trace_matrix_builder.trace_matrix_map.get_keys(),
            )
        )
        paths = get_paths_to_complete_graph(trace_ids, graph, 3)
        self.assertEqual(1, len(paths.get_keys()))
        self.assertEqual(1, len(paths["0-1"]))
        self.assertEqual([0, 2, 1], paths["0-1"][0])

    def test_contains_id(self):
        self.assertTrue(contains_trace_id(["0-1"], "0-1"))
        self.assertTrue(contains_trace_id(["0-1"], "1-0"))
        self.assertFalse(contains_trace_id(["0-1"], "0-2"))
