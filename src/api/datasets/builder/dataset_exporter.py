import os

import numpy as np
import pandas as pd

from api.datasets.builder.dataset_builder import DatasetBuilder, clean_level
from api.datasets.builder.transitive_trace_matrix_creator import parse_trace_id


def export_dataset(builder: DatasetBuilder):
    builder.create_dataset_export_folder()

    # Levels
    for level_index, level in enumerate(builder.levels):
        level_export_path = os.path.join(builder.path, "Artifacts", "Level_%d.csv" % level_index)
        level_cleaned = clean_level(level)
        level_cleaned.to_csv(level_export_path, index=False)

    # Relations.csv - Level_1_to_Level_3
    top_bottom_values = builder.trace_matrices["0-2"].matrix
    top_bottom_df = pd.DataFrame(top_bottom_values, columns=builder.levels[2]["id"])
    top_bottom_df["id"] = builder.levels[0]["id"]
    top_bottom_df.to_csv(os.path.join(builder.path, "Oracles", "Relations.csv"), index=False)

    # Trace Matrices
    for trace_id in builder.trace_matrices.keys():
        a_index, b_index = parse_trace_id(trace_id)
        matrix_file_name = "%d-%d.npy" % (a_index, b_index)
        matrix_file_path = os.path.join(builder.path, "Oracles", "TracedMatrices", matrix_file_name)
        matrix = builder.trace_matrices[trace_id].matrix
        np.save(matrix_file_path, matrix)
