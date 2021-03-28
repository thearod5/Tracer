from api.datasets.builder.structure_definition import get_structure_definition
from api.datasets.multi_level_artifacts import MultiLevelArtifacts
from tests.res.smart_test import SmartTest


class TestStructureDefinitionParser(SmartTest):
    level_cols = ["id", "text"]

    """
    get_structure_definition
    """

    def test_read_level_in_dataset_csv_file(self):
        dataset_name = "SAMPLE_EBT"
        structure: dict = get_structure_definition(dataset_name)

        # level 1
        level = MultiLevelArtifacts.read_artifact_level(structure["artifacts"]["1"])
        assert len(level) > 1, "Could not load top datasets: %d" % len(level)
        for col in self.level_cols:
            assert col in level.columns, "Expected %s in CACHE_COLUMNS: %s" % (
                col,
                level.columns,
            )
