"""
Creates a common interface for any type of table so that we can save it regardless of what type it is.
"""
from abc import ABC, abstractmethod

import pandas as pd


class ITable(ABC):
    """
    Table interface allowing for the saving of any sub-types
    """

    def __init__(self):
        self.table = pd.DataFrame()

    @abstractmethod
    def save(self, export_path: str):
        """
        Saves table's data source to given path
        :param export_path: str - the path where to save the file to
        :return: None
        """

    @abstractmethod
    def get_extension(self) -> str:
        """
        :return: str - the type of extension used in the underlying data model.
        """
