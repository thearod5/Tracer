"""
TODO
"""
from abc import ABC, abstractmethod

from api.datasets.dataset import Dataset
from api.technique.parser.data import TechniqueData
from api.technique.parser.itechnique_calculator import ITechniqueCalculator
from api.technique.parser.itechnique_definition import ITechniqueDefinition


class ITechnique(ABC):
    """
    TODO
    """

    def __init__(self, parameters: [str], components: [str]):
        self.definition = self.create_definition(parameters, components)
        self.calculator = self.create_calculator()

    @abstractmethod
    def create_definition(
        self, parameters: [str], components: [str]
    ) -> ITechniqueDefinition:
        """
        TODO
        :param parameters:
        :param components:
        :return:
        """

    @abstractmethod
    def create_calculator(self) -> ITechniqueCalculator:
        """
        TODO
        :return:
        """

    @staticmethod
    @abstractmethod
    def get_symbol() -> str:
        """
        TODO
        :return:
        """

    def calculate_technique_data(self, dataset: Dataset) -> TechniqueData:
        """
        TODO
        :param dataset:
        :return:
        """
        return self.calculator.calculate_technique_data(dataset)

    def get_name(self) -> str:
        """
        TODO
        :return:
        """
        return self.definition.get_name()
