from abc import abstractmethod
from typing import Callable, TypeVar, Generic

from api.datasets.dataset import Dataset
from api.technique.parser.data import TechniqueData

PipelineFunction = Callable[[TechniqueData], None]
Pipeline = [PipelineFunction]

GenericOutputData = TypeVar("GenericOutputData")


class TechniquePipeline(Generic[GenericOutputData]):
    """
    Manages the series of steps for a technique. Allows for abstraction between steps
    so that new steps can be easily formulated or pipelines extended.
    """

    def __init__(self, pipeline: Pipeline):
        if pipeline is None:
            self.pipeline = []
        self.pipeline = pipeline

    @abstractmethod
    def create_pipeline_data(self, dataset: Dataset):
        pass

    def run_pipeline_on_dataset(self, dataset: Dataset) -> GenericOutputData:
        data = self.create_pipeline_data(dataset)
        for p_func in self.pipeline:
            p_func(data)
        return data
