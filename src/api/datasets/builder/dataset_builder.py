import os

from igraph import Graph

from api.datasets.builder.level_parser import read_level_in_dataset
from api.datasets.builder.structure_definition_parser import get_structure_definition, get_path_to_dataset
from api.datasets.builder.transitive_trace_matrix_creator import TraceId2TraceMatrixMap, create_trace_matrix_map, \
    create_trace_matrix_graph
from api.datasets.cleaning.cleaners import clean_doc
from api.technique.variationpoints.aggregation.transitive_path_aggregation import dot_product_with_aggregation
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrices
from api.util.file_operations import create_if_not_exist


class DatasetBuilder:
    def __init__(self, dataset_name: str, create=False):
        self.name = dataset_name
        self.path = get_path_to_dataset(dataset_name)
        self.levels = []
        self.trace_matrices: TraceId2TraceMatrixMap = {}
        self.structure_file = get_structure_definition(dataset_name)
        self.defined_trace_matrices = [key for key in self.structure_file["traces"].keys() if
                                       self.structure_file["traces"][key] is not None]
        self.trace_graph: Graph = create_trace_matrix_graph(self.defined_trace_matrices,
                                                            len(self.structure_file["artifacts"]))

        if create:
            self.create_dataset()

    def create_dataset(self):
        self.create_levels()
        self.create_traced_matrices()
        self.remove_unimplemented_requirements()

    def create_levels(self):

        def create_level(path: str):
            return read_level_in_dataset(self.structure_file["artifacts"][path])

        level_indices = list(self.structure_file["artifacts"].keys())
        level_indices.sort()

        self.levels = list(map(create_level, level_indices))

    def create_traced_matrices(self):
        trace_matrix_map, trace_graph = create_trace_matrix_map(self.structure_file,
                                                                self.levels)
        self.trace_matrices = trace_matrix_map
        self.trace_graph = trace_graph

    def remove_unimplemented_requirements(self):  # Remove unimplemented requirements
        implemented_requirements = self.trace_matrices['0-2'].matrix.sum(axis=1) > 0
        for trace_id in self.trace_matrices.keys():
            if "0-" in trace_id:
                self.trace_matrices[trace_id].matrix = self.trace_matrices[trace_id].matrix[implemented_requirements, :]
            elif "-0" in trace_id:
                self.trace_matrices[trace_id].matrix = self.trace_matrices[trace_id].matrix[:, implemented_requirements]
        self.levels[0] = self.levels[0][implemented_requirements].dropna().reset_index(drop=True)

    def create_dataset_export_folder(self):
        required_folder = [os.path.join(self.path, "Artifacts"),
                           os.path.join(self.path, "Oracles"),
                           os.path.join(self.path, "Oracles", "TracedMatrices")]
        for folder in required_folder:
            create_if_not_exist(folder)


def clean_level(df):
    df = df.copy()
    assert "text" in df.columns, df.columns

    df["text"] = list(map(clean_doc, df["text"]))
    return df


def create_indirect_matrix(top_values, bottom_values):
    complement_similarity_matrices = SimilarityMatrices(top_values,
                                                        bottom_values)
    normalized = dot_product_with_aggregation(complement_similarity_matrices, max)
    return normalized
