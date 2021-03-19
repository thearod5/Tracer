from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix


class TraceMatrix:
    matrix: SimilarityMatrix
    top_name: str
    top_index: int
    top_artifact_ids: [int]

    bottom_name: str
    bottom_index: int
    bottom_artifact_ids: [int]

    def __init__(self, top_index, top_artifacts_ids, bottom_index, bottom_artifact_ids, matrix):
        self.top_index = top_index
        self.top_artifact_ids = top_artifacts_ids

        self.bottom_index = bottom_index
        self.bottom_artifact_ids = bottom_artifact_ids

        self.matrix = matrix
