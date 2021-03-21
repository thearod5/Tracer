"""
This module exports a parsed dataset under a common a common structure (e.g. folder system and naming schemes) that
allow the Tracer project API to run analysis on it.
"""
import os

import numpy as np
import pandas as pd

from api.datasets.builder.dataset_builder import DatasetBuilder
from api.datasets.builder.transitive_trace_matrix_creator import parse_trace_id
from api.datasets.cleaning.cleaners import clean_doc


def clean_level(raw_df):
    """
    For the `text` column in given DataFrame, clean each entry and returns DataFrame whose `text` column contains the
    cleaned artifacts.
    :param raw_df: the DataFrame containing the text documents to clean.
    :return: Copy of given DataFrame whose `text` columns only contains the cleaned strings.
    """
    raw_df = raw_df.copy()
    assert "text" in raw_df.columns, raw_df.columns

    raw_df["text"] = list(map(clean_doc, raw_df["text"]))
    return raw_df


def export_dataset(builder: DatasetBuilder):
    """
    Given a DatasetBuilder, this functions exports its artifacts and trace matrices into a standardized folder system
    and naming scheme utilized by the Tracer project.
    :param builder: The DatasetBuilder that has parsed a user-defined dataset
    :return: None
    """
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
