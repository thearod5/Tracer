from api.datasets.dataset import Dataset
from api.technique.definitions.sampled.definition import SampledTechniqueDefinition
from api.technique.definitions.transitive.calculator import TransitiveTechniqueData


class SampledTechniqueData(TransitiveTechniqueData):
    def __init__(self, dataset: Dataset, definition: SampledTechniqueDefinition):
        super().__init__(dataset, definition)
        self.technique = definition
