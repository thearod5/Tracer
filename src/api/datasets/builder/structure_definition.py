"""
The following module provides an API for parsing and reading `structure.json` files. These files are intended
to allow `DatasetBuilder` to find the necessary artifacts and traces in order to standardize the dataset's structure
so that the functions in this project can be used.

TODO: Define what is required in structure.json file
"""
import json
import os
from typing import Optional

from api.datasets.dataset import get_path_to_dataset

STRUCTURE_FILE_NAME = "structure.json"


class StructureDefinition:
    """
    Represents a class for parsing the structure files representing a machine-readable guide locating the
    artifacts and trace matrices for a dataset.
    """

    def __init__(self, dataset_name: Optional[str] = None, raw: Optional[dict] = None):
        """
        Reads and validates the structure.json file of the given dataset assumed to be in that "Datasets" root folder.
        :param dataset_name: the name of the folder in "Datasets" root folder containing the dataset assets
        :return: dict
        :TODO: add attributes to class instead of returning dictionary
        """
        if raw is not None:
            self.json = raw
        else:
            self.json = self._read_dataset_structure_file(dataset_name)

    def _read_dataset_structure_file(self, dataset_name: str) -> dict:
        path_to_dataset = get_path_to_dataset(dataset_name)
        structure_json = StructureDefinition.read_structure_file(path_to_dataset)

        top_level_branches = ["artifacts", "traces"]
        for top_branch in top_level_branches:
            assert top_branch in structure_json, "Could not find %s in %s" % (
                top_branch,
                dataset_name,
            )

        for key in structure_json["artifacts"]:
            relative_path = structure_json["artifacts"][key]
            final_path = (
                None
                if relative_path == ""
                else os.path.join(path_to_dataset, relative_path)
            )
            structure_json["artifacts"][key] = final_path

        for t_branch in structure_json["traces"]:
            relative_path = structure_json["traces"][t_branch]
            final_path = (
                None
                if relative_path == ""
                else os.path.join(path_to_dataset, relative_path)
            )
            structure_json["traces"][t_branch] = final_path

        return structure_json

    @staticmethod
    def read_structure_file(path_to_dataset: str) -> dict:
        """
        Reads structure.json file in given path to dataset.
        :param path_to_dataset: path to the parsed dataset containing a structure.json file
        :return: dict containing the contents of the structure.json file.
        """
        path_to_structure_file = os.path.join(path_to_dataset, STRUCTURE_FILE_NAME)
        with open(path_to_structure_file) as raw_structure_file:
            structure_file: dict = json.loads(raw_structure_file.read())
        return structure_file

    def is_valid_structure_file(self) -> bool:
        """
        Returns whether structure file contains all of required fields for structure.json files.
        :return: boolean - true if valid, false otherwise
        """
        top_branches = ["datasets", "traces"]
        artifact_branches = ["top", "middle", "bottom"]
        trace_branches = ["top-middle", "middle-bottom", "top-bottom"]

        return (
            StructureDefinition.contains_fields(self.json, top_branches)
            and StructureDefinition.contains_fields(
                self.json["datasets"], artifact_branches
            )
            and StructureDefinition.contains_fields(self.json["traces"], trace_branches)
        )

    @staticmethod
    def contains_fields(some_dict: dict, required_fields: [str]) -> bool:
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
