from api.datasets.builder.artifact_level_builder import ArtifactLevelBuilder
from api.datasets.builder.structure_definition import DatasetStructureDefinition
from tests.res.smart_test import SmartTest


class TestStructureDefinitionParser(SmartTest):
    level_cols = ["id", "text"]

    """
    get_structure_definition
    """

    def test_read_level_in_dataset_csv_file(self):
        dataset_name = "SAMPLE_EBT"
        structure: dict = DatasetStructureDefinition(dataset_name=dataset_name).json

        # level 1
        level = ArtifactLevelBuilder.read_artifact_level(structure["artifacts"]["1"])
        assert len(level) > 1, "Could not load top datasets: %d" % len(level)
        for col in self.level_cols:
            assert col in level.columns, "Expected %s in CACHE_COLUMNS: %s" % (
                col,
                level.columns,
            )
