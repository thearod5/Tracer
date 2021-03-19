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
    path_to_dataset = os.path.join(PATH_TO_DATASETS, dataset_name)
    path_to_structure_file = os.path.join(path_to_dataset, STRUCTURE_FILE_NAME)
    with open(path_to_structure_file) as raw_structure_file:
        structure_file: dict = json.loads(raw_structure_file.read())
    return structure_file


def get_path_to_dataset(dataset_name: str):
    return os.path.join(PATH_TO_DATASETS, dataset_name)


def is_valid_structure_file(structure_file: dict):
    top_branches = ["datasets", "traces"]
    artifact_branches = ["top", "middle", "bottom"]
    trace_branches = ["top-middle", "middle-bottom", "top-bottom"]

    return contains_branches(structure_file, top_branches) \
           and contains_branches(structure_file["datasets"], artifact_branches) \
           and contains_branches(structure_file["traces"], trace_branches)


def contains_branches(artifacts_structure: dict,
                      required_branches: [str],
                      n_allowed_invalid=0):
    n_invalid_branches = 0
    for a_branch in required_branches:
        if a_branch not in artifacts_structure:
            return False
        if artifacts_structure[a_branch] == "":
            n_invalid_branches = n_invalid_branches + 1
        if n_invalid_branches > n_allowed_invalid:
            return False
    return True
