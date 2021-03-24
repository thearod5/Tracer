"""
This module exports a parsed dataset under a common a common structure (e.g. folder system and naming schemes) that
allow the Tracer project API to run analysis on it.
"""

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
