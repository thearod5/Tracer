import numpy as np
from pandas import DataFrame

from api.constants.paths import PATH_TO_TEST_REQUIREMENTS
from api.datasets.builder.dataset_builder import DatasetBuilder, create_indirect_matrix
from api.datasets.builder.level_parser import read_level_in_dataset, parse_level_txt
from api.datasets.builder.structure_definition_parser import get_structure_definition, is_valid_structure_file, \
    contains_branches
from api.datasets.builder.trace_creator import get_trace_matrix_values
from api.util.file_operations import get_index_after_numbers
from tests.res.smart_test import SmartTest

VALID_PATH_PLACEHOLDER = "VALID_PATH_PLACEHOLDER"


class TestDatasetBuilder(SmartTest):
    level_cols = ["id", "text"]
    valid_artifacts = {
        "top": VALID_PATH_PLACEHOLDER,
        "middle": VALID_PATH_PLACEHOLDER,
        "bottom": VALID_PATH_PLACEHOLDER
    }
    valid_traces = {
        "top-middle": VALID_PATH_PLACEHOLDER,
        "middle-bottom": VALID_PATH_PLACEHOLDER,
        "top-bottom": VALID_PATH_PLACEHOLDER
    }

    def test_contains_branches(self):
        required_branches = ["top", "middle", "bottom"]
        assert contains_branches(self.valid_artifacts,
                                 required_branches)
        assert not contains_branches({}, required_branches)
        assert not contains_branches({
            "top": "",
            "bottom": "thing",
            "middle": ""
        }, required_branches)
        assert not contains_branches({
            "top": "",
            "bottom": "thing",
            "middle": ""
        }, required_branches, 1)

    def test_is_valid_structure_file(self):
        assert not is_valid_structure_file({})
        assert not is_valid_structure_file({"datasets": {}})
        assert not is_valid_structure_file({"traces": {}})
        assert not is_valid_structure_file({"datasets": {}, "traces": {}})
        assert is_valid_structure_file({"datasets": self.valid_artifacts,
                                        "traces": self.valid_traces})

    def test_read_level_in_dataset(self):
        dataset_name = "EasyClinic"
        structure: dict = get_structure_definition(dataset_name)

        level = read_level_in_dataset(structure["artifacts"]["0"])
        assert len(level) > 0, "Could not load top datasets"

        level = read_level_in_dataset(structure["artifacts"]["1"])
        assert len(level) == 20, "Could not load middle datasets %d " % len(level)

        level = read_level_in_dataset(structure["artifacts"]["2"])
        assert len(level) == 47, "Could not load bottom datasets %d " % len(level)

    def test_read_level_in_dataset_txt_file(self):
        d_name = "MockDataset"
        d_structure_def: dict = get_structure_definition(d_name)

        # level 1
        level = read_level_in_dataset(d_structure_def["artifacts"]["0"])
        self.assertEqual(len(level), 1, "Could not load top datasets: %d" % len(level))
        for col in self.level_cols:
            self.assertIn(col, level.columns, "Expected %s in CACHE_COLUMNS: %s" % (col, level.columns))

    def test_get_index_after_numbers(self):
        assert get_index_after_numbers("31.txt 420.txt") == 2
        assert get_index_after_numbers("DD-31 420.txt") == 5

    def test_parse_level_txt(self):
        path_to_level = PATH_TO_TEST_REQUIREMENTS
        level = parse_level_txt(path_to_level)
        assert len(level) > 0, "Expected non-empty list: %d" % len(level)
        for col in self.level_cols:
            assert col in level.columns, "Expected %s in CACHE_COLUMNS: %s" % (col, level.columns)

    def test_indirect_matrices_shape_with_missing_sources(self):
        dataset_name = "WARC"
        dataset_structure = DatasetBuilder(dataset_name)
        dataset_structure.create_dataset()

        top = dataset_structure.levels[0]
        middle = dataset_structure.levels[1]
        bottom = dataset_structure.levels[2]

        expected_top_middle_shape = (len(top), len(middle))
        expected_middle_bottom_shape = (len(middle), len(bottom))
        expected_top_bottom_shape = (len(top), len(bottom))

        test_matrix_shape(dataset_structure.trace_matrices["0-1"].matrix,
                          expected_top_middle_shape)
        test_matrix_shape(dataset_structure.trace_matrices["0-2"].matrix,
                          expected_top_bottom_shape)

        test_matrix_shape(dataset_structure.trace_matrices["1-2"].matrix,
                          expected_middle_bottom_shape)
        self.assertEqual(dataset_structure.trace_matrices["1-2"].matrix.shape, expected_middle_bottom_shape)

    """
    create_indirect_matrix
    """

    def test_create_indirect_matrix(self):
        a = np.array([[1, 1],
                      [0, 1]])
        b = np.array([[0, 1],
                      [0, 0]])
        c = create_indirect_matrix(a, b)
        assert c[0][0] == 0
        assert c[0][1] == 1
        assert c[0][0] == 0
        assert c[0][0] == 0


def test_matrix_shape(trace_matrix: np.ndarray, expected: (int, int)):
    assert trace_matrix.shape == expected, "Expected %s but got %s" % (expected, trace_matrix.shape)


def test_data_frame_shape(trace_matrix: DataFrame, expected: (int, int)):
    result = get_trace_matrix_values(trace_matrix)
    assert result.shape == expected, "Expected %s but got %s" % (expected, result)


def test_matrix_shape(result, expected: (int, int)):
    assert result.shape == expected, "Expected %s but got %s" % (expected, result)
