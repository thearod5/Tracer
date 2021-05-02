from typing import Tuple

from pandas import DataFrame

from api.constants.paths import PATH_TO_TEST_REQUIREMENTS
from api.datasets.builder.artifact_level_builder import ArtifactLevelBuilder
from api.datasets.builder.dataset_builder import DatasetBuilder
from api.datasets.builder.structure_definition import (
    DatasetStructureDefinition,
)
from api.extension.file_operations import get_index_after_numbers
from tests.res.smart_test import SmartTest

VALID_PATH_PLACEHOLDER = "VALID_PATH_PLACEHOLDER"


class TestDatasetBuilder(SmartTest):
    level_cols = ["id", "text"]
    valid_artifacts = {
        "top": VALID_PATH_PLACEHOLDER,
        "middle": VALID_PATH_PLACEHOLDER,
        "bottom": VALID_PATH_PLACEHOLDER,
    }
    valid_traces = {
        "top-middle": VALID_PATH_PLACEHOLDER,
        "middle-bottom": VALID_PATH_PLACEHOLDER,
        "top-bottom": VALID_PATH_PLACEHOLDER,
    }

    def test_read_level_in_dataset(self):
        dataset_name = "SAMPLE_EasyClinic"
        structure: dict = DatasetStructureDefinition(dataset_name=dataset_name).json

        level = ArtifactLevelBuilder.read_artifact_level(structure["artifacts"]["0"])
        assert len(level) > 0, "Could not load top datasets"

        level = ArtifactLevelBuilder.read_artifact_level(structure["artifacts"]["1"])
        assert len(level) == 20, "Could not load middle datasets %d " % len(level)

        level = ArtifactLevelBuilder.read_artifact_level(structure["artifacts"]["2"])
        assert len(level) == 47, "Could not load bottom datasets %d " % len(level)

    def test_read_level_in_dataset_txt_file(self):
        d_name = "MockDataset"
        d_structure_def: dict = DatasetStructureDefinition(dataset_name=d_name).json

        # level 1
        level = ArtifactLevelBuilder.read_artifact_level(
            d_structure_def["artifacts"]["0"]
        )
        self.assertEqual(len(level), 1, "Could not load top datasets: %d" % len(level))
        for col in self.level_cols:
            self.assertIn(
                col,
                level.columns,
                "Expected %s in CACHE_COLUMNS: %s" % (col, level.columns),
            )

    def test_get_index_after_numbers(self):
        assert get_index_after_numbers("31.txt 420.txt") == 2
        assert get_index_after_numbers("DD-31 420.txt") == 5

    def test_parse_level_txt(self):
        path_to_level = PATH_TO_TEST_REQUIREMENTS
        level = ArtifactLevelBuilder.parse_artifact_txt_file(path_to_level)
        assert len(level) > 0, "Expected non-empty list: %d" % len(level)
        for col in self.level_cols:
            assert col in level.columns, "Expected %s in CACHE_COLUMNS: %s" % (
                col,
                level.columns,
            )

    def test_indirect_matrices_shape_with_missing_sources(self):
        dataset_name = "SAMPLE_WARC"
        dataset_builder = DatasetBuilder(dataset_name)
        dataset_builder.build()

        top = dataset_builder.artifacts[0]
        middle = dataset_builder.artifacts[1]
        bottom = dataset_builder.artifacts[2]

        expected_top_middle_shape = (len(top), len(middle))
        expected_middle_bottom_shape = (len(middle), len(bottom))
        expected_top_bottom_shape = (len(top), len(bottom))

        assert_shapes_equal(
            dataset_builder.trace_matrix_map["0-1"].matrix, expected_top_middle_shape
        )
        assert_shapes_equal(
            dataset_builder.trace_matrix_map["0-2"].matrix, expected_top_bottom_shape
        )

        assert_shapes_equal(
            dataset_builder.trace_matrix_map["1-2"].matrix,
            expected_middle_bottom_shape,
        )
        self.assertEqual(
            dataset_builder.trace_matrix_map["1-2"].matrix.shape,
            expected_middle_bottom_shape,
        )


def assert_dataframe_shape_equals(trace_matrix: DataFrame, expected: Tuple[int, int]):
    result = trace_matrix.drop("id", axis=1).values
    assert result.shape == expected, "Expected %s but got %s" % (expected, result)


def assert_shapes_equal(result, expected: Tuple[int, int]):
    assert result.shape == expected, "Expected %s but got %s" % (expected, result)
