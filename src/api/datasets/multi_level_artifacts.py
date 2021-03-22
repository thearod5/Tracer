"""
This module represents the storage of artifacts in a Dataset.
"""
import os
from typing import List

import pandas as pd


class MultiLevelArtifacts:
    """
    Stores the list of artifacts in a Dataset
    """

    def __init__(self, path_to_dataset: str):
        path_to_artifacts = os.path.join(path_to_dataset, "Artifacts")

        artifact_files = list(
            filter(lambda f: f[0] != ".", os.listdir(path_to_artifacts))
        )
        artifact_files.sort()
        artifact_paths = list(
            map(lambda f: os.path.join(path_to_artifacts, f), artifact_files)
        )
        self.levels: List[pd.DataFrame] = list(map(pd.read_csv, artifact_paths))

    def __getitem__(self, key: int):
        return self.levels[key]

    def get_n_artifacts(self, level_index: int):
        """
        :return: int - the number of artifacts in the level of artifacts for given index
        """
        return len(self.levels[level_index])
