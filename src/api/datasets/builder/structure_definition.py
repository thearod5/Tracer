"""
The following module provides an API for parsing and reading `structure.json` files. These files are intended
to allow `DatasetBuilder` to find the necessary artifacts and traces in order to standardize the dataset's structure
so that the functions in this project can be used.

TODO: Define what is required in structure.json file
"""
import json
import os
from typing import Optional

from api.datasets.builder.dataset_path import get_path_to_dataset

STRUCTURE_FILE_NAME = "structure.json"


class DatasetStructure:
    """
    Represents a class for parsing the structure files representing a machine-readable guide locating the
    artifacts and trace matrices for a dataset. The following fields are required in a structure definition file:

    1. `artifacts` - dict - contains artifact level indices as indices and relative path to levels are values
    2. `traces` - dict - contains [source_artifact_level]-[target_artifact_level] as keys and relative path to file
    or folder containing trace links
    """

    ARTIFACT_KEY = "artifacts"
    TRACES_KEY = "traces"

    def __init__(self, dataset_name: Optional[str] = None, raw: Optional[dict] = None):
        if raw is not None:
            self.json = raw
        else:
            self.json = DatasetStructure._read_dataset_structure_file(dataset_name)

    @staticmethod
    def _read_dataset_structure_file(dataset_name: str) -> dict:
        """
        Reads and validates the structure.json file of the given dataset assumed to be in that "Datasets" root folder.
        :param dataset_name: the name of the folder in "Datasets" root folder containing the dataset assets
        :return: dict
        """
        path_to_dataset = get_path_to_dataset(dataset_name)
        structure_json = DatasetStructure._read_structure_file(path_to_dataset)

        top_level_branches = [
            DatasetStructure.ARTIFACT_KEY,
            DatasetStructure.TRACES_KEY,
        ]
        for top_branch in top_level_branches:
            assert top_branch in structure_json, "Could not find %s in %s" % (
                top_branch,
                dataset_name,
            )

        for key in structure_json[DatasetStructure.ARTIFACT_KEY]:
            relative_path = structure_json[DatasetStructure.ARTIFACT_KEY][key]
            final_path = (
                None
                if relative_path == ""
                else os.path.join(path_to_dataset, relative_path)
            )
            structure_json[DatasetStructure.ARTIFACT_KEY][key] = final_path

        for t_branch in structure_json[DatasetStructure.TRACES_KEY]:
            relative_path = structure_json[DatasetStructure.TRACES_KEY][t_branch]
            final_path = (
                None
                if relative_path == ""
                else os.path.join(path_to_dataset, relative_path)
            )
            structure_json[DatasetStructure.TRACES_KEY][t_branch] = final_path

        return structure_json

    @staticmethod
    def _read_structure_file(path_to_dataset: str) -> dict:
        """
        Reads structure.json file in given path to dataset.
        :param path_to_dataset: path to the parsed dataset containing a structure.json file
        :return: dict containing the contents of the structure.json file.
        """
        path_to_structure_file = os.path.join(path_to_dataset, STRUCTURE_FILE_NAME)
        with open(path_to_structure_file) as raw_structure_file:
            structure_file: dict = json.loads(raw_structure_file.read())
        return structure_file

    def __getitem__(self, item):
        return self.json[item]
