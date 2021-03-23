"""
TODO
"""
import os
from typing import List

import numpy as np
import pandas as pd

from api.constants.paths import PATH_TO_DATASETS, PATH_TO_SAMPLE_DATASETS
from api.datasets.multi_level_artifacts import MultiLevelArtifacts
from api.extension.type_checks import to_string


class Dataset:
    """
    Responsible for accessing parsed dataset resources (e.g. artifacts,  trace matrices).
    """

    def __init__(self, dataset_name: str):
        self.name = dataset_name
        self.path_to_dataset = get_path_to_dataset(dataset_name)

        self.artifacts = MultiLevelArtifacts(self.path_to_dataset)
        self.relations: pd.DataFrame = pd.read_csv(
            os.path.join(self.path_to_dataset, "Oracles", "Relations.csv")  # TODO: NOW
        )
        self.traced_matrices = {}

        self.load_trace_matrices()

        self.assert_valid_artifacts()  # implements D2

    def load_trace_matrices(self):
        """
        Read and stores the trace matrices of the parsed dataset
        :return: None
        """
        path_to_traced_matrices = os.path.join(self.path_to_dataset, "Oracles", "TracedMatrices")
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
        n_top_level = len(self.artifacts[0])
        n_middle_level = len(self.artifacts[1])
        n_bottom_level = len(self.artifacts[2])

        upper_shape = self.traced_matrices["0-1"].shape
        lower_shape = self.traced_matrices["1-2"].shape

        n_relation_bottom_level = len(self.relations.columns) - 1

        assert n_top_level == len(self.relations)
        assert n_bottom_level == n_relation_bottom_level, "Expected %d saw %d" % (
            n_bottom_level,
            n_relation_bottom_level,
        )
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


def get_path_to_dataset(dataset_name: str) -> str:
    """
    Returns the path to given dataset by looking in PATH_TO_DATASETS then in PATH_TO_SAMPLE_DATASETS if not found.
    If not dataset exist,
    :param dataset_name: The name of the folder containing the artifacts, traces, and structure.json file
    :return: str - path to dataset
    :raises:
        ValueError: if no dataset is found in PATH_TO_DATASETS or PATH_TO_SAMPLE_DATASETS
    """
    possible_folders = [PATH_TO_DATASETS, PATH_TO_SAMPLE_DATASETS]
    datasets_found: List[str] = []
    for p_folder in possible_folders:
        if not os.path.isdir(to_string(p_folder)):
            continue
        datasets_found = datasets_found + os.listdir(p_folder)
        if dataset_name in datasets_found:
            return os.path.join(to_string(p_folder), dataset_name)
    raise ValueError("%s is not one of %s" % (dataset_name, ",".join(datasets_found)))
