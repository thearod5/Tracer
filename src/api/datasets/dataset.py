"""
TODO
"""
import os
from typing import List

import numpy as np
import pandas as pd

from api.constants.techniques import ArtifactLevel
from api.datasets.builder.dataset_path import get_path_to_dataset


class Dataset:
    """
    Responsible for accessing parsed dataset resources (e.g. artifacts,  trace matrices).
    """

    def __init__(self, dataset_name: str):
        self.name = dataset_name
        self.path_to_dataset = get_path_to_dataset(dataset_name)

        self.artifacts = []
        self.traced_matrices = {}

        self.load_artifact_levels()
        self.load_trace_matrices()

        self.assert_valid_artifacts()

    def load_trace_matrices(self):
        """
        Read and stores the trace matrices of the parsed dataset
        :return: None
        """
        path_to_traced_matrices = os.path.join(
            self.path_to_dataset, "Oracles", "TracedMatrices"
        )
        trace_matrix_file_names = list(
            filter(lambda f: f[0] != ".", os.listdir(path_to_traced_matrices))
        )
        for file_name in trace_matrix_file_names:
            trace_id = file_name[:-4]
            path = os.path.join(path_to_traced_matrices, file_name)
            self.traced_matrices[trace_id] = np.load(path)

    def load_artifact_levels(self):
        path_to_artifacts = os.path.join(self.path_to_dataset, "Artifacts")
        artifact_files = list(
            filter(lambda f: f[0] != ".", os.listdir(path_to_artifacts))
        )
        artifact_files.sort()
        artifact_paths = list(
            map(lambda f: os.path.join(path_to_artifacts, f), artifact_files)
        )
        self.artifacts: List[ArtifactLevel] = list(map(pd.read_csv, artifact_paths))

    def assert_valid_artifacts(self):
        """
        TODO
        :return:
        """
        n_top_level = len(self.artifacts[0])
        n_middle_level = len(self.artifacts[1])
        n_bottom_level = len(self.artifacts[2])

        upper_trace_matrix_shape = self.traced_matrices["0-1"].shape
        lower_trace_matrix_shape = self.traced_matrices["1-2"].shape

        assert n_top_level == upper_trace_matrix_shape[0]
        assert n_middle_level == upper_trace_matrix_shape[1]
        assert n_middle_level == lower_trace_matrix_shape[0]
        assert n_bottom_level == lower_trace_matrix_shape[1]

    def get_oracle_matrix(self, source_level: int, target_level: int):
        """
        TODO
        :param source_level:
        :param target_level:
        :return:
        """
        oracle_id = "%s-%s" % (source_level, target_level)

        if oracle_id not in self.traced_matrices.keys():
            r_oracle_id = "%s-%s" % (target_level, source_level)

            if r_oracle_id not in self.traced_matrices.keys():
                raise Exception("no oracle exists between levels: %s" % oracle_id)
            return self.traced_matrices[r_oracle_id].T
        return self.traced_matrices[oracle_id]

    def get_n_artifacts(self, level_index: int):
        return len(self.artifacts[level_index])
