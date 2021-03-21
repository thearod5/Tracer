"""
TODO
"""
import os

import pandas as pd

from api.constants.paths import PATH_TO_DATASETS

ArtifactLevel = pd.DataFrame


class MultiLevelArtifacts:  # pylint: disable = too-few-public-methods
    """
    Represents a tri-layered set of datasets
    TODO: Add public methods
    """

    def __init__(self, dataset_name):
        path_to_artifacts = os.path.join(PATH_TO_DATASETS, dataset_name, "Artifacts")

        artifact_files = list(filter(lambda f: f[0] != ".", os.listdir(path_to_artifacts)))
        artifact_files.sort()
        artifact_paths = list(map(lambda f: os.path.join(path_to_artifacts, f), artifact_files))
        self.levels: [ArtifactLevel] = list(map(pd.read_csv, artifact_paths))

        self.n_top_artifacts = len(self.levels[0])
        self.n_bottom_artifacts = len(self.levels[-1])
