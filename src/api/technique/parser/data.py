"""
TODO
"""
from typing import Union

from api.datasets.dataset import Dataset
from api.metrics.models import ScoringTable
from api.technique.parser import itechnique_definition
from api.technique.parser.itechnique_definition import ITechniqueDefinition
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix


class TechniqueData:
    """
    The base class for describing the technique_data that persists between a technique's
    computational steps.
    """

    def __init__(self, dataset: Dataset, technique: ITechniqueDefinition):
        self.dataset: Dataset = dataset
        self.technique: itechnique_definition = technique
        self.similarity_matrix: Union[
            SimilarityMatrix, None
        ] = None  # matrix of simlarity scores between source & target artifacts

    def get_scoring_table(self) -> ScoringTable:
        """
        TODO
        :return:
        """
        assert self.similarity_matrix is not None, "similarity table was not computed"
        return create_similarity_scoring_table_from_matrix(
            self.dataset,
            self.technique.source_level,
            self.technique.target_level,
            self.similarity_matrix,
        )

    def get_similarity_matrix(self) -> SimilarityMatrix:
        """
        TODO
        :return:
        """
        return self.similarity_matrix

    def with_matrix(self, similarity_matrix: SimilarityMatrix):
        """
        TODO
        :param similarity_matrix:
        :return:
        """
        self.similarity_matrix = similarity_matrix
        return self


def create_similarity_scoring_table_from_matrix(
    dataset: Dataset,
    source_level: int,
    target_level: int,
    similarity_matrix: SimilarityMatrix,
) -> ScoringTable:
    """
    Returns ScoringTable containing the predictions from similarity matrix and oracle values from given dataset
    :param dataset: dataset containing the oracle values
    :param source_level: the index of the level that queries are for
    :param target_level: the index of the level that is being queried against
    :param similarity_matrix: the predicted values between source and target levels
    :return: two columns table representing predicted and actual values for queries between source and target levels
    """
    predicted_values = similarity_matrix.flatten()
    oracle_matrix = dataset.get_oracle_matrix(source_level, target_level)
    oracle_values = oracle_matrix.flatten()

    assert len(oracle_values) == len(
        predicted_values
    ), "oracle values does not match predicted values"

    return ScoringTable(predicted_values, oracle_values)
