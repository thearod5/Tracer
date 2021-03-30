"""
The central location from where to get the path to a dataset's folder.
"""
import os
from typing import List

from api.constants.paths import PATH_TO_DATASETS, PATH_TO_SAMPLE_DATASETS
from api.extension.type_checks import to_string


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
    if PATH_TO_DATASETS == "":
        raise RuntimeError(
            "PATH_TO_DATASETS in .env is empty and %s is not a sample dataset."
            % dataset_name
        )
    raise ValueError(
        "Could not find %s, not one of %s" % (dataset_name, ",".join(datasets_found))
    )
