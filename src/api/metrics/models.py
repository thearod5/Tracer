from abc import ABC, abstractmethod

import numpy
import numpy as np
import pandas as pd
from sklearn.preprocessing import minmax_scale

from api.constants.preprocessing import METRIC_COLNAME, SCORE_COLNAME, ALL_METRIC_NAMES, DATASET_COLNAME, \
    DATASET_COLUMN_ORDER, AP_COLNAME, AUC_COLNAME, Data
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix

SIMILARITY_MATRIX_EXTENSION = ".npy"
SimilaritiesType = numpy.ndarray


class ITable(ABC):
    def __init__(self):
        self.table = pd.DataFrame()

    @abstractmethod
    def export(self, export_path: str):
        pass

    @abstractmethod
    def get_extension(self) -> str:
        pass


class ScoringTable(ITable):
    """
    Data class for storing prediction and oracle values used for evaluation of techniques.
    """

    def __init__(self, y_pred: np.ndarray, y_true: np.ndarray):
        super().__init__()
        self.values: SimilarityMatrix = np.vstack([y_pred, y_true]).T

    def flatten(self) -> SimilaritiesType:
        return self.values.flatten()

    def export(self, export_path: str):
        raise NotImplementedError()

    def get_extension(self) -> str:
        raise NotImplementedError()


class Metrics:
    """
    Stores all metrics for some query.
    """

    def __init__(self, ap: float, auc: float, lag: float):
        self.ap = ap
        self.auc = auc
        self.lag = lag

    def __sub__(self, other):
        assert isinstance(other, Metrics)
        ap_delta = self.ap - other.ap
        auc_delta = self.auc - other.auc
        lag_delta = self.lag - other.lag
        return Metrics(ap=ap_delta, auc=auc_delta, lag=lag_delta)


class Table(ITable):  # todo: move this into its own file
    """
    Wrapper class encapsulating common operations on data frames.
    """

    def __init__(self):  # implements MT1
        super().__init__()
        self.table = pd.DataFrame()

    def add(self, entries, other: dict = None, create_index=False, index_name='query_index'):  # implements MT2
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

        entries_dict = list(map(lambda m: vars(m), entries))  # created dictionary from given object
        for m_index, m in enumerate(entries_dict):
            m.update(other)
            if create_index:
                m.update({index_name: m_index})

        self.table = self.table.append(entries_dict, ignore_index=True)

    def format_table(self):
        self.table = format_data(self.table)

    def export(self, export_path):  # implements MT3
        self.table.to_csv(export_path, index=False)

    def update(self, table: ITable):
        return pd.concat([self.table, table.table])

    def get_extension(self) -> str:
        return ".csv"

    def melt_metrics(self):
        id_vars = [col for col in self.table.columns if col not in ALL_METRIC_NAMES]
        self.table = pd.melt(self.table, id_vars=id_vars, var_name=METRIC_COLNAME, value_name=SCORE_COLNAME)

    def scale_col(self, col_name: str, by: [str], new_col_name=None, drop_old=False, inverted=False):
        """
        Performs min-max scaling on given column name, renames new values to scaled_col_name.
        If none is given appends `normalized` to metric_name
        :param col_name: the name of the metric in the table to scale
        :param by: list of col name to group by before scaling
        :param new_col_name: name of the column containing scaled values
        :param drop_old: if true removes the column without the scaled numbers
        :param inverted: metrics scores will be inverted so that new_score = 1 - old_score
        :return: None - MetricTable is modified
        """
        new_col_name = new_col_name if new_col_name is not None else "%s_%s" % (col_name, "normalized")
        sections = self.table.groupby(by).groups
        new_sections = []
        for group_id, group_indices in sections.items():
            dataset_df = self.table.iloc[group_indices].copy()
            dataset_df[new_col_name] = minmax_scale(dataset_df[col_name])
            new_sections.append(dataset_df)

        self.table = pd.concat(new_sections, axis=0)

        if inverted:
            inverted_col_name = "%s_%s" % (new_col_name, "inverted")
            self.table[inverted_col_name] = 1 - self.table[new_col_name]

        if drop_old:
            self.table = self.table.drop(col_name, axis=1)
            if inverted:
                self.table = self.table.drop(new_col_name, axis=1)


def format_data(data: Data, for_presentation=False):
    if DATASET_COLNAME in data.columns:
        dataset = list(set(DATASET_COLUMN_ORDER + list(data[DATASET_COLNAME].unique())))
        data[DATASET_COLNAME] = pd.Categorical(data[DATASET_COLNAME], categories=dataset)
    data = data.reset_index(drop=True)
    defined_sort_columns = [col for col in COLUMN_ORDER if col in data.columns]
    other_columns = [col for col in data.columns if col not in defined_sort_columns]
    data = data[defined_sort_columns + other_columns]
    data = data.sort_values(by=defined_sort_columns)

    if for_presentation:
        presentation_map = {AP_COLNAME: "mAP",
                            AUC_COLNAME: "AUC",
                            LAG_NORMALIZED_INVERTED_COLNAME: "LagNormInverted"}
        if METRIC_COLNAME in data.columns:
            data[METRIC_COLNAME] = data[METRIC_COLNAME].replace(presentation_map)
        data.columns = list(map(lambda s: "".join(list(map(lambda s_0: s_0.title(), s.split("_")))), data.columns))

    return data.round(n_sig_figs)
