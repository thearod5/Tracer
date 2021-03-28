"""
This module is used to parse raw datasets into Tracer-compatible datasets that are can be used by the generic functions
established throughout the project. Note, datasets must have their top level artifacts as level 0 and their main target
artifacts as level 2. This is due to the fact target artifacts without a connecting source artifact are ignored

:TODO:
    * Make a more consistent rule for dropping unlinked target artifacts.
"""
import os

import numpy as np
import pandas as pd
from igraph import Graph

from api.datasets.builder.dataset_exporter import clean_level
from api.datasets.builder.structure_definition import (
    StructureDefinition,
    get_path_to_dataset,
)
from api.datasets.builder.transitive_trace_matrix_creator import (
    TraceId2TraceMatrixMap,
    create_trace_matrix_graph,
    create_trace_matrix_map,
    parse_trace_id,
)
from api.datasets.multi_level_artifacts import MultiLevelArtifacts
from api.extension.file_operations import create_if_not_exist


class DatasetBuilder:
    """
    Module Builds given dataset expected to be found in PATH_TO_DATASETS folder and to have a
    `structure_definition.json` file telling the builder where the artifacts and traces are.
    """

    def __init__(self, dataset_name: str, create=False):
        self.name = dataset_name
        self.path = get_path_to_dataset(dataset_name)
        self.levels = []
        self.trace_matrices: TraceId2TraceMatrixMap = {}
        self.structure_file = StructureDefinition.get_structure_definition(dataset_name)
        self.defined_trace_matrices = [
            key
            for key in self.structure_file["traces"].keys()
            if self.structure_file["traces"][key] is not None
        ]
        self.trace_graph: Graph = create_trace_matrix_graph(
            self.defined_trace_matrices, len(self.structure_file["artifacts"])
        )
        if create:
            self.create_dataset()

    def create_dataset(self):
        """
        Encapsulates all of the sub-operations required to parse and clean a dataset.
        :return: None
        """
        self.create_levels()
        # create trace matrices
        trace_matrix_map, trace_graph = create_trace_matrix_map(
            self.structure_file, self.levels
        )
        self.trace_matrices = trace_matrix_map
        self.trace_graph = trace_graph
        self.remove_unimplemented_requirements()

        print(trace_matrix_map)

    def create_levels(self):
        """
        For each level defined in the structure.json file this parses, cleans, and stored the level.
        :return: None
        """

        def create_level(path: str):
            return MultiLevelArtifacts.read_artifact_level(
                self.structure_file["artifacts"][path]
            )

        level_indices = list(self.structure_file["artifacts"].keys())
        level_indices.sort()

        self.levels = list(map(create_level, level_indices))

    def remove_unimplemented_requirements(self):  # Remove unimplemented requirements
        """
        Looks into the trace matrix between levels 0 and 2 and removes all the artifacts in level 2 which out a link
        to level 0.
        :return: None
        """
        implemented_requirements = self.trace_matrices["0-2"].matrix.sum(axis=1) > 0
        for trace_id in self.trace_matrices.keys():
            if "0-" in trace_id:
                self.trace_matrices[trace_id].matrix = self.trace_matrices[
                    trace_id
                ].matrix[implemented_requirements, :]
            elif "-0" in trace_id:
                self.trace_matrices[trace_id].matrix = self.trace_matrices[
                    trace_id
                ].matrix[:, implemented_requirements]
        self.levels[0] = (
            self.levels[0][implemented_requirements].dropna().reset_index(drop=True)
        )

    def create_dataset_export_folder(self):
        """
        Creates the required folder structure for datasets including:
        * Artifacts
        * Oracles
        * Oracles/TracedMatrices
        :return:
        """
        required_folder = [
            os.path.join(self.path, "Artifacts"),
            os.path.join(self.path, "Oracles"),
            os.path.join(self.path, "Oracles", "TracedMatrices"),
        ]
        for folder in required_folder:
            create_if_not_exist(folder)

    def export_dataset(self):
        """
        Given a DatasetBuilder, this functions exports its artifacts and trace matrices into a standardized folder
        system and naming scheme utilized by the Tracer project.
        :return: None
        """
        self.create_dataset_export_folder()

        # Levels
        for level_index, level in enumerate(self.levels):
            level_export_path = os.path.join(
                self.path, "Artifacts", "Level_%d.csv" % level_index
            )
            level_cleaned = clean_level(level)
            level_cleaned.to_csv(level_export_path, index=False)

        # Relations.csv - Level_1_to_Level_3
        top_bottom_values = self.trace_matrices["0-2"].matrix
        top_bottom_df = pd.DataFrame(top_bottom_values, columns=self.levels[2]["id"])
        top_bottom_df["id"] = self.levels[0]["id"]
        top_bottom_df.to_csv(
            os.path.join(self.path, "Oracles", "Relations.csv"), index=False
        )

        # Trace Matrices
        for trace_id in self.trace_matrices.keys():
            a_index, b_index = parse_trace_id(trace_id)
            matrix_file_name = "%d-%d.npy" % (a_index, b_index)
            matrix_file_path = os.path.join(
                self.path, "Oracles", "TracedMatrices", matrix_file_name
            )
            matrix = self.trace_matrices[trace_id].matrix
            np.save(matrix_file_path, matrix)
