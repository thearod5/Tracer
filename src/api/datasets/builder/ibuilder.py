"""
The following module constructs a small interface for building dataset related documents.
"""
from abc import abstractmethod


class IBuilder:
    """
    Required builders to have a method so create the document(s) and to be able to export them
    """

    def __init__(self):
        self.export_paths = []

    @abstractmethod
    def build(self):
        """
        Constructs the document(s) builder is responsible for
        :return: None
        """

    @abstractmethod
    def export(self, path_to_dataset: str):
        """
        Export built documents given path
        :param path_to_dataset: paths details should be specified by child builders.
        :return:
        """
