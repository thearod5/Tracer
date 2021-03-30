"""
This module is used to parse raw datasets into Tracer-compatible datasets that are can be used by the generic functions
established throughout the project. Note, datasets must have their top level artifacts as level 0 and their main target
artifacts as level 2. This is due to the fact target artifacts without a connecting source artifact are ignored
"""
import os
from typing import Optional

from api.constants.techniques import ArtifactLevel
from api.datasets.builder.artifact_level_builder import ArtifactLevelBuilder
from api.datasets.builder.get_dataset_path import get_path_to_dataset
from api.datasets.builder.ibuilder import IBuilder
from api.datasets.builder.structure_definition import (
    DatasetStructureDefinition,
)
from api.datasets.builder.trace_matrix import TraceId2TraceMatrixMap
from api.datasets.builder.trace_matrix_builder import (
    TraceMatrixBuilder,
)
from api.extension.file_operations import create_if_not_exist


class DatasetBuilder(IBuilder):
    """
    Module builds artifacts and corresponding trace matrices for given dataset using the paths found in
    `structure.json` file telling the builder where the artifacts and traces are. Datasets are expected to be found
    in PATH_TO_DATASETS or PATH_TO_SAMPLE_DATASETS.
    """

    def __init__(
        self,
        dataset_name: str,
    ):
        super().__init__()
        self.path_to_dataset = get_path_to_dataset(dataset_name)
        self.structure_definition = DatasetStructureDefinition(
            dataset_name=dataset_name
        )
        self.artifact_builder: Optional[ArtifactLevelBuilder] = ArtifactLevelBuilder(
            self.structure_definition
        )
        self.trace_matrix_builder: Optional[TraceMatrixBuilder] = TraceMatrixBuilder(
            structure_definition=self.structure_definition
        )
        self.trace_matrix_map: Optional[TraceId2TraceMatrixMap] = None
        self.artifacts: Optional[ArtifactLevel] = None

    def build(self):
        """
        Builds artifacts levels and their corresponding trace matrices.
        :return: None
        """
        self.artifact_builder.build()
        self.artifacts = self.artifact_builder.artifacts
        self.trace_matrix_builder.set_artifact_levels(self.artifacts)

        self.trace_matrix_builder.build()
        self.trace_matrix_map = self.trace_matrix_builder.trace_matrix_map

    def export(self, path_to_dataset: Optional[str] = None):
        """
        Given a DatasetBuilder, this functions exports its artifacts and trace matrices into a standardized folder
        system and naming scheme utilized by the Tracer project.
        :return: None
        """
        self._create_dataset_export_folder()
        self.artifact_builder.export(self.path_to_dataset)
        self.trace_matrix_builder.export(self.path_to_dataset)

    def _create_dataset_export_folder(self):
        """
        Creates the required folder structure for datasets including:
        * Artifacts
        * Oracles
        * Oracles/TracedMatrices
        :return:
        """
        required_folder = [
            os.path.join(self.path_to_dataset, "Artifacts"),
            os.path.join(self.path_to_dataset, "Oracles"),
            os.path.join(self.path_to_dataset, "Oracles", "TracedMatrices"),
        ]
        for folder in required_folder:
            create_if_not_exist(folder)
