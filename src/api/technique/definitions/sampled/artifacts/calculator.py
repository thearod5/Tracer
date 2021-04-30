"""
TODO
"""
from api.datasets.dataset import Dataset
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.definitions.sampled.sampler import sample_indices
from api.technique.definitions.sampled.technique_data import SampledTechniqueData
from api.technique.definitions.transitive.calculator import (
    TRANSITIVE_TECHNIQUE_PIPELINE,
    TransitiveTechniqueCalculator,
)


def sample_matrices(data: SampledTechniqueData):
    """
    TODO
    :param data:
    :return:
    """
    indices_to_keep_agg = []
    for matrix in data.transitive_matrices[:-1]:  # no sampling on last matrix
        # sample percentage of intermediate indices
        n_transitive_artifacts = matrix.shape[1]
        indices_to_keep = sample_indices(
            n_transitive_artifacts, data.technique.sample_percentage
        )
        indices_to_keep_agg.append(indices_to_keep)

    for boundary_index, boundary_indices in enumerate(indices_to_keep_agg):
        boundary_indices.sort()
        boundary_indices = indices_to_keep_agg[boundary_index]

        # select artifacts using sampled indices
        data.transitive_matrices[boundary_index] = data.transitive_matrices[
            boundary_index
        ][:, boundary_indices]
        data.transitive_matrices[boundary_index + 1] = data.transitive_matrices[
            boundary_index + 1
        ][boundary_indices, :]


SAMPLED_ARTIFACTS_PIPELINE = TRANSITIVE_TECHNIQUE_PIPELINE.copy()
SAMPLED_ARTIFACTS_PIPELINE.insert(1, sample_matrices)


class SampledArtifactsTechniqueCalculator(TransitiveTechniqueCalculator):
    """
    TODO
    """

    def __init__(self, definition: SampledTechniqueDefinition):
        super().__init__(definition, SAMPLED_ARTIFACTS_PIPELINE)

    def create_pipeline_data(self, dataset: Dataset) -> SampledTechniqueData:
        """
        TODO
        :param dataset:
        :return:
        """
        return SampledTechniqueData(dataset, self.definition)
