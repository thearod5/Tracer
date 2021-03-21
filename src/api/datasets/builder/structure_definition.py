"""
The following module provides an API for parsing and reading `structure.json` files. These files are intended
to allow `DatasetBuilder` to find the necessary artifacts and traces in order to standardize the dataset's structure
so that the functions in this project can be used.

TODO: Define what is required in structure.json file
"""
import json
import os

from api.constants.paths import PATH_TO_DATASETS

STRUCTURE_FILE_NAME = "structure.json"


def get_structure_definition(dataset_name: str):
    """
    Reads and validates the structure.json file of the given dataset assumed to be in that "Datasets" root folder.
    :param dataset_name: the name of the folder in "Datasets" root folder containing the dataset assets
    :return: dict
    """
    path_to_dataset = get_path_to_dataset(dataset_name)
    structure_json = read_structure_file(dataset_name)

    top_level_branches = ["artifacts", "traces"]
    for top_branch in top_level_branches:
        assert top_branch in structure_json, "Could not find %s in %s" % (top_branch, dataset_name)

    for key in structure_json["artifacts"]:
        relative_path = structure_json["artifacts"][key]
        final_path = None if relative_path == "" else os.path.join(path_to_dataset, relative_path)
        structure_json["artifacts"][key] = final_path

    for t_branch in structure_json["traces"]:
        relative_path = structure_json["traces"][t_branch]
        final_path = None if relative_path == "" else os.path.join(path_to_dataset, relative_path)
        structure_json["traces"][t_branch] = final_path
    return structure_json


def read_structure_file(dataset_name: str) -> dict:
    """
    Attempts to load structure.json file in given dataset_name under the PATH_TO_DATASETS directory.
    :param dataset_name: the name of the folder containing the structure.json file
    :return: dict containing the contents of the structure.json file.
    """
    path_to_dataset = os.path.join(PATH_TO_DATASETS, dataset_name)
    path_to_structure_file = os.path.join(path_to_dataset, STRUCTURE_FILE_NAME)
    with open(path_to_structure_file) as raw_structure_file:
        structure_file: dict = json.loads(raw_structure_file.read())
    return structure_file


def get_path_to_dataset(dataset_name: str):
    """
    Returns the path to given user-defined dataset_name
    :param dataset_name: The name of the folder containing the artifacts, traces, and structure.json file
    :return: str - path to dataset
    """
    return os.path.join(PATH_TO_DATASETS, dataset_name)


def is_valid_structure_file(structure_file: dict):
    """
    Returns whether given structure file contains all of required fields for structure.json files.
    :param structure_file: the contents of a dataset's structure.json file
    :return: boolean - true if valid, false otherwise
    """
    top_branches = ["datasets", "traces"]
    artifact_branches = ["top", "middle", "bottom"]
    trace_branches = ["top-middle", "middle-bottom", "top-bottom"]

    return contains_fields(structure_file, top_branches) \
           and contains_fields(structure_file["datasets"], artifact_branches) \
           and contains_fields(structure_file["traces"], trace_branches)


def contains_fields(some_dict: dict,
                    required_fields: [str]):
    """
    Returns whether given dictionary contains required fields.
    :param some_dict: a python dictionary
    :param required_fields: list of fields that must be in given dictionary
    :return: boolean
    """
    for a_branch in required_fields:
        if a_branch not in some_dict:
            return False
    return True
