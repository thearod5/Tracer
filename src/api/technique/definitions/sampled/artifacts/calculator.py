from api.datasets.dataset import Dataset
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.definitions.sampled.sampler import sample_indices
from api.technique.definitions.sampled.technique_data import SampledTechniqueData
from api.technique.definitions.transitive.calculator import TransitiveTechniqueCalculator, \
    INTERMEDIATE_TECHNIQUE_PIPELINE


def sample_matrices(data: SampledTechniqueData):
    indices_to_keep_agg = []
    for matrix in data.transitive_matrices[:-1]:
        n_transitive_artifacts = matrix.shape[1]
        indices_to_keep = sample_indices(n_transitive_artifacts, data.technique.sample_percentage)
        indices_to_keep_agg.append(indices_to_keep)

    for boundary_index in range(len(indices_to_keep_agg)):
        boundary_indices = indices_to_keep_agg[boundary_index]
        data.transitive_matrices[boundary_index] = data.transitive_matrices[boundary_index][:, boundary_indices]
        data.transitive_matrices[boundary_index + 1] = data.transitive_matrices[boundary_index + 1][
                                                       boundary_indices, :]


SAMPLED_ARTIFACTS_PIPELINE = INTERMEDIATE_TECHNIQUE_PIPELINE.copy()
SAMPLED_ARTIFACTS_PIPELINE.insert(1, sample_matrices)


class SampledArtifactsTechniqueCalculator(TransitiveTechniqueCalculator):
    def __init__(self, definition: SampledTechniqueDefinition):
        super().__init__(definition, SAMPLED_ARTIFACTS_PIPELINE)

    def create_pipeline_data(self, dataset: Dataset) -> SampledTechniqueData:
        return SampledTechniqueData(dataset, self.definition)
