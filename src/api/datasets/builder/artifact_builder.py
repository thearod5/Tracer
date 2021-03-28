"""
This module represents the storage of artifacts in a Dataset.
"""
import os
from typing import List

import pandas as pd

from api.datasets.builder.ibuilder import IBuilder
from api.datasets.builder.structure_definition import DatasetStructure
from api.datasets.builder.trace_parser import get_document_delimiter
from api.datasets.cleaning.cleaners import clean_level
from api.extension.file_operations import get_non_empty_lines


class ArtifactBuilder(IBuilder):
    """
    Responsible for building artifacts in a dataset.
    """

    def __init__(self, structure_definition: DatasetStructure):
        super().__init__()
        self.structure_definition = structure_definition
        self.artifacts: List[pd.DataFrame] = []

    def build(self):
        def create_level(path: str):
            return ArtifactBuilder.read_artifact_level(
                self.structure_definition["artifacts"][path]
            )

        level_indices = list(self.structure_definition["artifacts"].keys())
        level_indices.sort()

        self.artifacts = list(map(create_level, level_indices))

    def export(self, path_to_dataset: str):
        for level_index, level in enumerate(self.artifacts):
            level_export_path = os.path.join(
                path_to_dataset, "Artifacts", "Level_%d.csv" % level_index
            )
            level_cleaned = clean_level(level)
            level_cleaned.to_csv(level_export_path, index=False)
            self.export_paths.append(level_export_path)

    def __getitem__(self, key: int):
        return self.artifacts[key]

    def get_n_artifacts(self, level_index: int):
        """
        :return: int - the number of artifacts in the level of artifacts for given index
        """
        return len(self.artifacts[level_index])

    @staticmethod
    def read_artifact_level(path_to_artifacts: str, contains_ids_in_file=False):
        """
        Returns a DataFrame containing the id and text of each artifact found in given path.
        :param path_to_artifacts: The path to the folder or file containing the artifacts.
        :param contains_ids_in_file: If given path to artifacts is a file, defines whether the given path to file also
        contains the ids of the artifacts.
        :return: DataFrame - containing `id` and `text` of artifacts
        """
        if os.path.isfile(path_to_artifacts):
            if ".txt" in path_to_artifacts:
                artifact_level = ArtifactBuilder.parse_artifact_txt_file(
                    path_to_artifacts
                )
            elif ".csv" in path_to_artifacts:
                artifact_level = pd.read_csv(path_to_artifacts)
            else:
                raise ValueError("Could not identify file type: %s" % path_to_artifacts)
        else:

            assert os.path.isdir(path_to_artifacts), (
                "Given path is not a directory: %s" % path_to_artifacts
            )
            artifact_level = pd.DataFrame(columns=["id", "text"])
            files_in_folder = list(
                filter(lambda f: f[0] != ".", os.listdir(path_to_artifacts))
            )
            for file_name in files_in_folder:
                path_to_file = os.path.join(path_to_artifacts, file_name)

                try:
                    with open(path_to_file) as file:
                        text = file.read()
                except ValueError:
                    with open(path_to_file, encoding="ISO-8859-1") as file:
                        text = file.read()

                if contains_ids_in_file:
                    # Remove any identifier information
                    _, delimiter_index = get_document_delimiter(text, return_index=True)
                    text = text[delimiter_index:]

                # add to df
                item = {"id": file_name.strip(), "text": text.strip()}
                artifact_level = artifact_level.append(item, ignore_index=True)

        artifact_level["id"] = artifact_level["id"].astype(str)
        artifact_level["text"] = artifact_level["text"].astype(str)
        artifact_level = artifact_level.dropna()
        return artifact_level

    @staticmethod
    def parse_artifact_txt_file(path_to_file: str):
        """
        Given a file defining a list of artifacts, extracts the id and text of each artifact.
        :param path_to_file: path to file containing artifact definitions.
        :return: DataFrame - containing `id` and `text` columns for each artifact found.
        """
        assert os.path.isfile(path_to_file), "File not found: %s" % path_to_file
        artifacts_df = pd.DataFrame(columns=["id", "text"])
        with open(path_to_file) as level_file:
            level_contents = level_file.read()
            level_lines = get_non_empty_lines(level_contents)
            for line in level_lines:
                line_delimiter = get_document_delimiter(line)
                line_split = line.split(line_delimiter)
                a_id, a_body = line_split[0], line_delimiter.join(line_split[1:])
                artifacts_df = artifacts_df.append(
                    {"id": a_id.strip(), "text": a_body.strip()}, ignore_index=True
                )
        return artifacts_df
