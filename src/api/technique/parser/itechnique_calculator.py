"""
TODO
"""

from abc import abstractmethod
from typing import Generic

from api.datasets.dataset import Dataset
from api.experiment.cache import Cache
from api.technique.parser.itechnique_definition import ITechniqueDefinition
from api.technique.parser.pipeline import TechniquePipeline, GenericOutputData


class ITechniqueCalculator(
    Generic[GenericOutputData], TechniquePipeline[GenericOutputData]
):
    """
    Interface for interacting with TechniqueCalculators. Includes:
    Responsibility is to manage calculations using pipeline by leveraging the cache.
    """

    def __init__(self, technique_definition: ITechniqueDefinition, pipeline):
        super().__init__(pipeline)
        self.definition = technique_definition

    def calculate_technique_data(self, dataset: Dataset) -> GenericOutputData:
        """
        The runs the set pipeline on technique_data created from create_pipeline_data and returns result.
        If subclasses are stochastic calculators override this method and implement to implement
        management of cached states when cache is on. This function will always recalculate techniques
        if cache is off.
        :param dataset: contains the artifacts levels to run the technique on.
        :return: the technique_data after mutated by pipeline functions
        """
        if Cache.CACHE_ON and not self.definition.contains_stochastic_technique():
            if Cache.is_cached(dataset, self.definition):
                data = self.create_pipeline_data(dataset)
                data.similarity_matrix = Cache.get_similarities(
                    dataset, self.definition
                )
            else:
                data = self.run_pipeline_on_dataset(dataset)
                Cache.store_similarities(
                    dataset, self.definition, data.similarity_matrix
                )
        else:
            data = self.run_pipeline_on_dataset(dataset)
        return data

    @abstractmethod
    def create_pipeline_data(self, dataset: Dataset) -> GenericOutputData:
        """
        TODO
        :param dataset:
        :return:
        """
