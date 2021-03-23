"""
Creates a class for storing similarity scores alongside the oracle values used for creating metrics.
"""
import numpy as np

from api.constants.dataset import SimilarityMatrix
from api.constants.techniques import SimilaritiesType
from api.tables.itable import ITable


class ScoringTable(ITable):
    """
    Data class for storing prediction and oracle values used for evaluation of techniques.
    """

    def __init__(self, y_pred: np.ndarray, y_true: np.ndarray):
        super().__init__()
        self.values: SimilarityMatrix = np.vstack([y_pred, y_true]).T

    def flatten(self) -> SimilaritiesType:
        """
        TODO
        :return:
        """
        return self.values.flatten()

    def save(self, export_path: str):
        """
        Saves the current table to the give path.
        :param export_path: str - where to save the table to.
        :return: None
        """
        raise NotImplementedError()

    def get_extension(self) -> str:
        """
        Returns the type of file that is used to store the table.
        :return: str - the extension of the storage file.
        """
        raise NotImplementedError()
