"""
The Table module serves as a proxy for all of the post or pre processing operations that a user may need.
All of the operations are wrapped in the Table object below.
"""
import os
from typing import Optional, Tuple

import pandas as pd

from api.constants.processing import (
    AP_COLNAME,
    AUC_COLNAME,
    COLUMN_ORDER,
    DATASET_COLNAME,
    DATASET_COLUMN_ORDER,
    LAG_NORMALIZED_INVERTED_COLNAME,
    METRIC_COLNAME,
    N_SIG_FIGS,
)
from api.tables.itable import ITable


class Table(ITable):
    """
    Proxy class encapsulating pre and post processing operations for generic tables.
    """

    def __init__(
        self, table: Optional[pd.DataFrame] = None, path_to_table: Optional[str] = None
    ):
        super().__init__()
        self.table = pd.DataFrame() if table is None else table
        if path_to_table is not None:
            self.table = pd.read_csv(path_to_table)

    def add(
        self, entries, other: dict = None, create_index=False, index_name="query_index"
    ):
        """
        Converts given entries to dictionary values and appends dictionary in other before
        adding to the table.
        :param entries: list of objects each representing an entry
        :param other: key-value pairs that are appended to each entry in entries
        :param create_index: adds a columns specifying the index of each metric in given list
        :param index_name: the name of column that will hold the index
        :return: objects is modified None is returned
        """
        if other is None:
            other = {}

        entries_dict = list(map(vars, entries))  # created dictionary from given object
        for item_index, metric_item in enumerate(entries_dict):
            metric_item.update(other)
            if create_index:
                metric_item.update({index_name: item_index})

        self.table = self.table.append(entries_dict, ignore_index=True)

    def sort_cols(self) -> "Table":
        """
        Sorts columns of table using the constants in api/constants
        :return: Table - copy of this table but with sort applied
        """
        if DATASET_COLNAME in self.table.columns:
            dataset = list(
                set(DATASET_COLUMN_ORDER + list(self.table[DATASET_COLNAME].unique()))
            )
            self.table[DATASET_COLNAME] = pd.Categorical(
                self.table[DATASET_COLNAME], categories=dataset
            )
        data = self.table.reset_index(drop=True)
        defined_columns_in_sort_order = [
            col for col in COLUMN_ORDER if col in data.columns
        ]
        undefined_columns = [
            col for col in data.columns if col not in defined_columns_in_sort_order
        ]
        return Table(data[defined_columns_in_sort_order + undefined_columns])

    def format_table(self, names_title_case=False) -> "Table":
        """
        1. Sorts datasets using constants defined in api/constants
        2. Sorts column order of data
        3. Formats numerical data to a fixed amount of sig figs (see api/constants)
        :param data: the source data
        :param names_title_case: whether the names of metrics and columns should be lower case
        :return: DataFrame with modifications specified
        """

        data = self.sort_cols().table

        if names_title_case:
            presentation_map = {
                AP_COLNAME: "mAP",
                AUC_COLNAME: "AUC",
                LAG_NORMALIZED_INVERTED_COLNAME: "LagNormInverted",
            }
            if METRIC_COLNAME in data.columns:
                data[METRIC_COLNAME] = data[METRIC_COLNAME].replace(presentation_map)
            else:
                raise ValueError(
                    "for_presentation flag set but could not find column:"
                    % METRIC_COLNAME
                )

            data.columns = list(
                map(
                    lambda s: "".join(list(map(lambda s_0: s_0.title(), s.split("_")))),
                    data.columns,
                )
            )

        rounded_df = data.round(N_SIG_FIGS)
        return Table(rounded_df)

    def save(self, export_path: str):
        """
        Saves the current table to a csv at given path.
        :param export_path: where to save the table to
        :return: None
        """
        self.table.to_csv(export_path, index=False)

    def get_extension(self) -> str:
        """
        :return: str - the extension of the underlying data model
        """
        return ".csv"

    def split(
        self, left: pd.Series, right: pd.Series
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Returns a tuple of two dataframes where the first contains the trues of given boolean list and the latter the
        falses
        :param left: the boolean mask for choosing the left data frame
        :param right: the boolean mask for choosing the right data frame
        :return:
        """
        return self.table[left], self.table[right]

    @staticmethod
    def aggregate_intermediate_files(path_to_intermediate_files: str) -> "Table":
        """
        Combines all .csv files in path_to_components and exports it to aggregate_export_path.
        :param path_to_intermediate_files: path to folder containing one or more intermediary files
        :return: None
        """
        aggregate_df = None
        for intermediate_file_name in os.listdir(path_to_intermediate_files):
            if intermediate_file_name[0] == ".":
                continue
            intermediate_df = pd.read_csv(
                os.path.join(path_to_intermediate_files, intermediate_file_name)
            )
            intermediate_df[DATASET_COLNAME] = intermediate_file_name[:-4]
            aggregate_df = (
                intermediate_df
                if aggregate_df is None
                else pd.concat([aggregate_df, intermediate_df])
            )
        return Table(aggregate_df)
