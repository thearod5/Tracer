"""
TODO
"""
import os

import numpy as np
import pandas as pd

from api.constants.paths import PATH_TO_ROOT, PATH_TO_DATASETS
from api.datasets.multi_level_artifacts import MultiLevelArtifacts


class Dataset:
    """
    TODO
    """

    def __init__(self, dataset_name: str):  # implements D1
        self.name = dataset_name
        self.artifacts = MultiLevelArtifacts(dataset_name)  # implements D3
        self.relations: Relations = pd.read_csv(
            os.path.join(PATH_TO_DATASETS, dataset_name, "Oracles", "Relations.csv"))
        self.traced_matrices = {}
        self.path_to_dataset = os.path.join(PATH_TO_ROOT, dataset_name)
        self.load_trace_matrices()

        self.assert_valid_artifacts()  # implements D2

    def load_trace_matrices(self):
        """
        TODO
        :return:
        """
        path_to_traced_matrices = os.path.join(PATH_TO_DATASETS, self.name, "Oracles", "TracedMatrices")
        trace_matrix_file_names = list(filter(lambda f: f[0] != ".", os.listdir(path_to_traced_matrices)))
        for file_name in trace_matrix_file_names:
            trace_id = file_name[:-4]
            path = os.path.join(path_to_traced_matrices, file_name)
            self.traced_matrices[trace_id] = np.load(path)

    def assert_valid_artifacts(self):
        """
        TODO
        :return:
        """
        n_top_level = len(self.artifacts.levels[0])
        n_middle_level = len(self.artifacts.levels[1])
        n_bottom_level = len(self.artifacts.levels[2])

        upper_shape = self.traced_matrices["0-1"].shape
        lower_shape = self.traced_matrices["1-2"].shape

        n_relation_bottom_level = len(self.relations.columns) - 1

        assert n_top_level == len(self.relations)
        assert n_bottom_level == n_relation_bottom_level, "Expected %d saw %d" % (
            n_bottom_level, n_relation_bottom_level)
        assert n_top_level == upper_shape[0]
        assert n_middle_level == upper_shape[1]
        assert n_middle_level == lower_shape[0]
        assert n_bottom_level == lower_shape[1]

    def get_y_true(self) -> np.ndarray:
        """
        TODO
        :return:
        """
        return self.relations.drop("id", axis=1).values.flatten()

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


Relations = pd.DataFrame
