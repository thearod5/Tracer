from abc import ABC, abstractmethod

from api.datasets.dataset import Dataset
from api.technique.parser.data import TechniqueData
from api.technique.parser.itechnique_calculator import ITechniqueCalculator
from api.technique.parser.itechnique_definition import ITechniqueDefinition


class ITechnique(ABC):
    def __init__(self, parameters: [str], components: [str]):
        self.definition = self.create_definition(parameters, components)
        self.calculator = self.create_calculator()

    @abstractmethod
    def create_definition(self, parameters: [str], components: [str]) -> ITechniqueDefinition:
        pass

    @abstractmethod
    def create_calculator(self) -> ITechniqueCalculator:
        pass

    @staticmethod
    @abstractmethod
    def get_symbol() -> str:
        pass

    def calculate_technique_data(self, dataset: Dataset) -> TechniqueData:
        return self.calculator.calculate_technique_data(dataset)

    def get_name(self) -> str:
        return self.definition.get_name()
