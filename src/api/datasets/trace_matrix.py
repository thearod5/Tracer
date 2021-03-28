"""
TODO
"""
from typing import Dict

import pandas as pd

from api.constants.dataset import SimilarityMatrix
from api.datasets.builder.trace_parser import (
    create_trace_matrix_values_from_trace_list,
    parse_trace_file,
)


class TraceMatrix:  # pylint: disable=too-few-public-methods
    """
    TODO: Documentation
    TODO: Add public methods or used a namedtuple. Then, remove pylint bypass
    """

    matrix: SimilarityMatrix
    top_name: str
    top_index: int
    top_artifact_ids: [int]

    bottom_name: str
    bottom_index: int
    bottom_artifact_ids: [int]

    # pylint: disable=too-many-arguments
    def __init__(
        self, top_index, top_artifacts_ids, bottom_index, bottom_artifact_ids, matrix
    ):
        # TODO: Too many arguments, separate for modularity
        self.top_index = top_index
        self.top_artifact_ids = top_artifacts_ids

        self.bottom_index = bottom_index
        self.bottom_artifact_ids = bottom_artifact_ids

        self.matrix = matrix

    def transpose(self) -> "TraceMatrix":
        """
        Returns a copy of this TraceMatrix with artifacts and traces transposed so that top artifacts become the bottom
        ones and the bottom ones become the top.
        :return:
        """
        return TraceMatrix(
            top_index=self.bottom_index,
            top_artifacts_ids=self.bottom_artifact_ids,
            bottom_index=self.top_index,
            bottom_artifact_ids=self.top_artifact_ids,
            matrix=self.matrix.T,
        )

    @staticmethod
    def create_trace_matrix_from_path(
        top_artifacts_ids: pd.Series,
        top_index: int,
        bottom_artifacts_ids: pd.Series,
        bottom_index: int,
        path_to_trace_list: str,
    ) -> "TraceMatrix":
        """
        TODO
        :param top_artifacts_ids:
        :param top_index:
        :param bottom_artifacts_ids:
        :param bottom_index:
        :param path_to_trace_list:
        :return:
        """
        trace_list = parse_trace_file(path_to_trace_list)
        trace_matrix_values = create_trace_matrix_values_from_trace_list(
            top_artifacts_ids, bottom_artifacts_ids, trace_list
        )
        trace_matrix = TraceMatrix(
            top_index,
            top_artifacts_ids,
            bottom_index,
            bottom_artifacts_ids,
            trace_matrix_values,
        )
        return trace_matrix


TraceId2TraceMatrixMap = Dict[
    str, TraceMatrix
]  # for retrieving TraceMatrix values at east
