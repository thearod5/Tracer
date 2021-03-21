from igraph import Graph

from api.datasets.builder.structure_definition import get_structure_definition
from api.datasets.builder.trace_parser import get_document_delimiter, get_traces_in_line, \
    is_valid_trace_list, \
    parse_trace_file, create_trace_matrix_values_from_trace_list, get_index_of_next_alpha_char, \
    get_delimiter_in_segment, \
    get_traces_in_trace_file_content
from api.datasets.builder.transitive_trace_matrix_creator import create_trace_matrix_graph, find_all_paths
from api.experiment.file_operations import get_index_after_number_with_extension
from tests.res.smart_test import SmartTest


class TestTraceCreator(SmartTest):
    """
    get_document_delimiter
    """

    def test_get_document_delimiter_colon(self):
        dataset_name = "EasyClinic"
        structure: dict = get_structure_definition(dataset_name)
        with open(structure["traces"]["0-1"]) as top_trace_file:
            delimiter = get_document_delimiter(top_trace_file.read())
            assert delimiter == ":", delimiter

    def test_get_document_delimiter_tab(self):
        dataset_name = "WARC"

        structure: dict = get_structure_definition(dataset_name)
        with open(structure["traces"]["0-1"]) as top_trace_file:
            delimiter = get_document_delimiter(top_trace_file.read())
            assert delimiter == "\t", delimiter

    """
    get_document_delimiter
    """

    def test_get_document_delimiter_space(self):
        delimiter = get_document_delimiter("DD-23 LlaCoordinate.java")
        assert delimiter == " ", delimiter

    def test_get_document_delimiter_with_space_with_extension(self):
        self.assertEqual(" ", get_document_delimiter("31.txt 32.txt "))

    def test_get_document_delimiter_with_dash(self):
        delimiter = get_document_delimiter("SRS 75 - Body start here")
        self.assertEqual("-", delimiter)

    """
    get_index_of_next_alpha_char
    """

    def test_get_index_of_next_alpha_char_with_dash(self):
        self.assertEqual(6, get_index_of_next_alpha_char("abc - def", 3))

    def test_get_index_of_next_alpha_char_with_tab(self):
        self.assertEqual(10, get_index_of_next_alpha_char("NFR01.txt\tSRS49.txt", 9))

    def test_get_index_of_next_alpha_char_with_extensions(self):
        self.assertEqual(7, get_index_of_next_alpha_char("31.txt 32.txt", 6))

    def test_get_index_after_number_with_space_with_extension(self):
        self.assertEqual(6, get_index_after_number_with_extension('31.txt 32.txt'))

    def test_get_index_after_number_with_tab_with_extension(self):
        self.assertEqual(9, get_index_after_number_with_extension('NFR01.txt\tSRS49.txt'))

    """
    get_delimiter_in_segment
    """

    def test_get_delimiter_in_segment_high_precedence(self):
        self.assertEqual("-", get_delimiter_in_segment(" - "))

    def test_get_delimiter_in_segment_low_precedence(self):
        self.assertEqual(" ", get_delimiter_in_segment("abc def"))

    """
    test_get_traces_for_dataset
    """

    def test_get_traces_ec(self):
        dataset_name = "EasyClinic"
        traces = test_get_traces_for_dataset(dataset_name)
        assert len(traces) > 25, len(traces)

    def test_get_traces_warc(self):
        dataset_name = "WARC"
        test_get_traces_for_dataset(dataset_name)

    """
    get_traces_in_trace_file_content
    """

    def test_get_traces_in_trace_file_content_without_delimiter(self):
        content = "13"
        traces = get_traces_in_trace_file_content(content)
        self.assertEqual(0, len(traces))

    def test_get_traces_in_trace_file_content_with_delimiter(self):
        content = "13 SomeClass.java"
        traces = get_traces_in_trace_file_content(content)
        self.assertEqual(1, len(traces))

    def test_get_traces_in_trace_file_content_with_empty_lines(self):
        content = "13 SomeClass.java\n\n"
        traces = get_traces_in_trace_file_content(content)
        self.assertEqual(1, len(traces))

        content = "abd def\n\nabc def"
        traces = get_traces_in_trace_file_content(content)
        self.assertEqual(2, len(traces))

    """
    get_traces_in_line
    """

    def test_get_traces_in_line(self):
        traces = get_traces_in_line("source.txt:target1.txt target2.txt")
        self.assertEqual(2, len(traces))
        self.assert_traces(traces)

    def test_get_traces_in_line_space(self):
        traces = get_traces_in_line("source.txt target1.txt target2.txt")
        self.assertEqual(2, len(traces))
        self.assert_traces(traces)

    def test_get_traces_in_line_missing_target(self):
        traces = get_traces_in_line("source.txt: ")
        self.assertEqual(0, len(traces))

    def test_get_traces_in_linewith_tab(self):
        line = "ABCsd	DEF ABC"
        traces = get_traces_in_line(line)
        self.assertEqual(2, len(traces))

    def assert_traces(self, traces):
        self.assertEqual("source.txt", traces[0][0])
        self.assertEqual("target1.txt", traces[0][1])
        self.assertEqual("source.txt", traces[1][0])
        self.assertEqual("target2.txt", traces[1][1])

    """
    is_valid_trace_list
    """

    def test_is_valid_trace_list(self):
        self.assertFalse(is_valid_trace_list("str"))
        self.assertTrue(is_valid_trace_list([("R1", "C1")]))
        self.assertFalse(is_valid_trace_list([("R1", "C1"), ("R1")]))
        self.assertFalse(is_valid_trace_list([("R1")]))
        self.assertFalse(is_valid_trace_list([["R1"]]))

    """
    create_trace_matrix_from_trace_list
    """

    def test_create_trace_matrix_from_trace_list(self):
        top_ids = ["R1", "R2"]
        bottom_ids = ["C1", "C2"]
        trace_list = [("R2", "C1")]
        trace_matrix = create_trace_matrix_values_from_trace_list(top_ids, bottom_ids, trace_list)

        self.assertEqual(0, trace_matrix[0][0])
        self.assertEqual(0, trace_matrix[0][1])
        self.assertEqual(1, trace_matrix[1][0])
        self.assertEqual(0, trace_matrix[1][1])

    """
        find_all_paths
        """

    def test_find_all_paths_one(self):
        graph: Graph = create_trace_matrix_graph([], 1)
        paths = find_all_paths(graph, 0, 0)
        self.assertEqual(1, len(paths))
        self.assertEqual(1, len(paths[0]))
        self.assertEqual(0, paths[0][0])

    def test_find_all_paths_two_complete(self):
        graph: Graph = create_trace_matrix_graph(["0-1"], 2)
        paths = find_all_paths(graph, 0, 1)
        self.assertEqual(1, len(paths))
        self.assertEqual([0, 1], paths[0])

    def test_find_all_paths_two_empty(self):
        graph: Graph = create_trace_matrix_graph([], 2)
        paths = find_all_paths(graph, 0, 1)
        self.assertEqual(0, len(paths))

    def test_find_all_paths_three_complete(self):
        graph: Graph = create_trace_matrix_graph(["0-2", "0-1", "1-2"], 3)
        paths = find_all_paths(graph, 0, 1)
        self.assertEqual(2, len(paths))
        self.assertEqual([0, 1], paths[0])
        self.assertEqual([0, 2, 1], paths[1])

    def test_find_all_paths_three_incomplete(self):
        graph: Graph = create_trace_matrix_graph(["0-2"], 3)
        paths = find_all_paths(graph, 0, 1)
        self.assertEqual(0, len(paths))

    def test_find_all_paths_four_incomplete(self):
        traces = ["1-2", "0-2", "2-3", "1-0", "0-3", "1-3"]
        graph: Graph = create_trace_matrix_graph(traces, 4)
        paths = find_all_paths(graph, 1, 2)
        self.assertEqual(5, len(paths))
        self.assertTrue([1, 0, 2] in paths)
        self.assertTrue([1, 2] in paths)
        self.assertTrue([1, 3, 2] in paths)
        self.assertTrue([1, 0, 3, 2] in paths)
        self.assertTrue([1, 3, 0, 2] in paths)


def test_get_traces_for_dataset(dataset_name: str):
    structure: dict = get_structure_definition(dataset_name)
    traces = parse_trace_file(structure["traces"]["0-1"])

    for trace in traces:
        source, target = trace
        assert len(source) > 1, "Source contains empty string"
        assert len(target) > 1, "Target contains empty string"

    return traces
