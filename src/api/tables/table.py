"""
The Table module serves as a proxy for all of the post or pre processing operations that a user may need.
All of the operations are wrapped in the Table object below.
"""
import os
from typing import List, Optional, Tuple

import pandas as pd

from api.constants.processing import (
    ALL_METRIC_NAMES,
    COLUMN_ORDER,
    DATASET_COLNAME,
    METRIC_COLNAME,
    N_SIG_FIGS,
    TECHNIQUE_TYPE_COLNAME,
    TECHNIQUE_TYPE_SORT_ORDER,
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

    def add(
        self, entries, other: dict = None, create_index=False, index_name="query_index"
    ) -> "Table":
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
        return self.table

    def sort(self, dataset_column_order: List[str]) -> "Table":
        """
        Sorts values by dataset, technique_type, and metrics then sorts columns
        Sort orders are defined by the constants in src/constants
        :return: Table - copy of this table but with sort applied
        """
        data = Table(self.table.copy())

        # TODO: This is dependent on order
        if METRIC_COLNAME in self.table.columns:
            data = data.to_categorical(METRIC_COLNAME, ALL_METRIC_NAMES)
            data = data.sort_values(group_names=[METRIC_COLNAME], axis=0)

        if TECHNIQUE_TYPE_COLNAME in self.table.columns:
            data = data.to_categorical(
                TECHNIQUE_TYPE_COLNAME, TECHNIQUE_TYPE_SORT_ORDER
            )
            data = data.sort_values(group_names=[TECHNIQUE_TYPE_COLNAME], axis=0)
        if DATASET_COLNAME in self.table.columns:
            data = data.to_categorical(DATASET_COLNAME, dataset_column_order)
            data = data.sort_values(group_names=[DATASET_COLNAME], axis=0)

        defined_columns_in_sort_order = [
            col for col in COLUMN_ORDER if col in data.table.columns
        ]
        undefined_columns = [
            col
            for col in data.table.columns
            if col not in defined_columns_in_sort_order
        ]
        return Table(data.table[defined_columns_in_sort_order + undefined_columns])

    def sort_values(self, group_names: List[str], axis: int) -> "Table":
        """
        Sorts the rows of the table using specified values along axis
        :param group_names: the col names or row values to sort by
        :param axis: 0 if cols 1 if rows
        :return:
        """
        return Table(self.table.sort_values(by=group_names, axis=axis))

    def to_categorical(self, col_name: str, col_value_order: List[str]) -> "Table":
        """
        Converts the given column into a categorical one which can be used for sorting later.
        :param col_name: the name of the column to convert
        :param col_value_order: the order of the categories in the specified column
        :return: Table
        """
        data = self.table.copy()
        data[col_name] = pd.Categorical(data[col_name], categories=col_value_order)
        return Table(data)

    def to_title_case(self, exclude: Optional[List[str]] = None) -> "Table":
        """
        Converted every column and categorical value to their their title case representation.
        :param exclude: list of columns to exclude from this processing
        :return:
        """
        data = self.table.copy()
        exclude = [] if exclude is None else exclude
        for col_name in data.columns:
            if (
                data[col_name].dtype not in ["int64", "float64"]
                and col_name not in exclude
            ):
                data[col_name] = data[col_name].apply(split_and_format)
        data.columns = list(map(split_and_format, data.columns))
        return Table(data)

    def col_values_to_upper(self, col_name: str) -> "Table":
        """
        Converts values in given column to upper case.
        :param col_name: name of columns whose values will be transformed
        :return: Table
        """
        data = self.table.copy()
        data[col_name] = data[col_name].apply(lambda c_value: c_value.upper())
        return Table(data)

    def round(self, sig_figs=N_SIG_FIGS) -> "Table":
        """
        Rounds numerical columns to the significant figures given sig figs.
        :return:
        """
        return Table(self.table.round(sig_figs))

    def save(self, export_path: str) -> "Table":
        """
        Saves the current table to a csv at given path.
        :param export_path: where to save the table to
        :return: None
        """
        self.table.to_csv(export_path, index=False)
        return self

    def format_percents_for_latex(self, to_int=False):
        """
        For any any containing "percent", its values are put into the range of [0,100] and a "\\%" precedes them.
        :param to_int: whether percents should be put into integer formats
        :return:
        """
        data = self.table.copy()
        for col in data.columns:
            if "percent" in col.lower():
                data[col] = data[col].apply(
                    lambda f: f"{int(f * 100) if to_int else f * 100}\\%"
                )
        return Table(data)

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

    def __add__(self, other) -> "Table":
        """
        Vertically stacks other table on top of this one.
        :param other: Table - table to stack on the bottom
        :return: Table - combined values of this table (on top) and other (on bottom)
        """
        assert isinstance(other, Table), "is not of type Table"
        intersecting_columns = [
            c for c in self.table.columns if c in other.table.columns
        ]
        copy = self.table.copy()
        joined = copy.merge(other.table, on=intersecting_columns)
        return Table(joined)

    def drop_duplicate_columns(self):
        """
        Copy of table with all duplicate columns removed.
        This can be useful after joins where extra columns are kept.
        :return: Table - Copy of table values
        """
        data = self.table.copy()
        data = data.loc[:, ~data.columns.duplicated()]
        return Table(data)


def split_and_format(name: str, delimiter="_"):
    """
    Returns the title-cased version of name after being seperated by given delimiter
    :param name: the name containing delimiter to be formatted
    :param delimiter: the delimiter separating the parts in name
    :return:
    """
    return "".join(list(map(lambda p: p.title(), name.split(delimiter))))
