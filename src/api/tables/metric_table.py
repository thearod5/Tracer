"""
This module is responsible to creating a proxy-class encapsulating all pre/post-processing operations defined
on a metric table.
"""

from typing import List, Optional

import pandas as pd
from scipy.stats import spearmanr
from sklearn.preprocessing import minmax_scale

from api.constants.processing import (
    ALL_METRIC_NAMES,
    AP_COLNAME,
    CORE_METRIC_NAMES,
    CORRELATION_COLNAME,
    DATASET_COLNAME,
    Data,
    INVERTED_METRICS,
    LAG_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
    META_COLS,
    METRIC_COLNAME,
    NAME_COLNAME,
    N_SIG_FIGS,
    PERCENT_BEST_COLNAME,
    P_VALUE_COLNAME,
    RANK_COLNAME,
    RELATIVE_GAIN_COLNAME,
    TECHNIQUE_COLNAME,
    TECHNIQUE_TYPE_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
    VARIATION_POINT_COLNAME,
)
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.extension.experiment_types import ExperimentTraceType
from api.tables.table import Table

ESPILON = 0.001


class MetricTable(Table):
    """
    Represents a table containing:
    * Metrics as columns (required)
    * Technique identifying information (optional)
    """

    def __init__(
        self, table: Optional[Data] = None, path_to_table: Optional[str] = None
    ):
        super().__init__(table, path_to_table=path_to_table)

    def find_direct_best_techniques(self, metric_name=AP_COLNAME) -> "MetricTable":
        """
        Fins the highest performing direct techniques
        :param metric_name: the metric which to declare a best from.
        TODO: How to deal with ties
        :return: Table
        """
        data = self.table.copy()
        direct_data = data[self.get_technique_type_mask(DIRECT_ID)]
        best_technique_df = get_best_rows(direct_data, metric_name)
        return MetricTable(best_technique_df)

    def find_best_transitive_techniques(self, metric_name=AP_COLNAME) -> "MetricTable":
        """
        Finds the transitive techniques that performed the best on given metric table.
        Note, only techniques without transitive traces are considered.
        :param metric_name: the metric from which to decide a best
        :return: Table
        """
        data = self.table.copy()
        query_mask = self.get_none_traced_mask() & self.get_technique_type_mask(
            TRANSITIVE_ID
        )
        best_techniques_df = get_best_rows(
            data[query_mask],
            metric_name,
        )
        return MetricTable(best_techniques_df)

    def find_best_combined_techniques(self, metric_name=AP_COLNAME) -> "MetricTable":
        """
        Returns the set of indices corresponding to the best combined, non-traced techniques.
        :param metric_name: the metric from which to decide a best
        :return: Table
        """
        data = self.table.copy()
        query_mask = self.get_none_traced_mask() & self.get_technique_type_mask(
            HYBRID_ID
        )
        best_techniques_df = get_best_rows(
            data[query_mask],
            metric_name,
        )
        return MetricTable(best_techniques_df)

    def get_direct_best_indices(self, metric_name=AP_COLNAME) -> List[int]:
        """
        Calculates the gain in metrics between the direct best of each dataset and the scores for given
        techniques on each dataset
        :param metric_name: the metric which to declare a best from.
        TODO: How to deal with ties
        :return: Table
        """
        best_rows = self.find_direct_best_techniques(metric_name=metric_name)
        return best_rows.table.index

    def get_transitive_best_indices(self, metric_name=AP_COLNAME) -> List[int]:
        """
        Calculates the gain in metrics between the direct best of each dataset and the scores for given
        techniques on each dataset
        :param metric_name: the metric from which to decide a best
        :return: Table
        """
        data = self.table.copy()
        query_mask = self.get_none_traced_mask() & self.get_technique_type_mask(
            TRANSITIVE_ID
        )
        best_rows = get_best_rows(
            data[query_mask],
            metric_name,
        )
        return best_rows.index

    def get_best_combined_no_traces_indices(self, metric_name=AP_COLNAME) -> List[int]:
        """
        Returns the set of indices corresponding to the best combined, non-traced techniques.
        :param metric_name: the metric from which to decide a best
        :return: Table
        """

        return self.find_best_combined_techniques(metric_name).table.index

    def get_best_combined_traces_indices(self, metric_name=AP_COLNAME) -> List[int]:
        """
        Returns the set of indices corresponding to the best combined, traced techniques.
        :param metric_name: the metric from which to decide a best
        :return: Table
        """
        data = self.table.copy()
        query_mask = ~self.get_none_traced_mask() & self.get_technique_type_mask(
            HYBRID_ID
        )
        best_rows = get_best_rows(
            data[query_mask],
            metric_name,
        )
        return best_rows.index

    def get_technique_indices(self, technique_definition: str) -> List[int]:
        """
        Calculates the gain between given technique and direct best
        :param technique_definition:
        :return:
        """
        return self.table[self.table[NAME_COLNAME] == technique_definition].index

    def get_none_traced_mask(self) -> bool:
        """
        Returns boolean mask for all rows whose trace type is NONE (e.g. uses no transitive traces).
        :return: boolean mask
        """
        return (
            self.table[TRANSITIVE_TRACE_TYPE_COLNAME]
            == ExperimentTraceType.NONE.value.lower()
        )

    def get_technique_type_mask(self, technique_type: str) -> bool:
        """
        Returns mask on table for rows which match given technique_type
        :param technique_type:
        :return:
        """
        return self.table[TECHNIQUE_TYPE_COLNAME] == technique_type

    def create_ranks(
        self, rank_col=AP_COLNAME, new_col_name=RANK_COLNAME
    ) -> "MetricTable":
        """
        For each dataset and trace type, create ranks with 1 corresponding to highest map score
        :param rank_col: str - the name of the column to be used for ranking
        :param new_col_name: str - the name of the new column containing the ranks
        :return:
        """
        data = self.table.copy()
        aggregated_rank_df = None

        rank_groups = [
            DATASET_COLNAME,
            TECHNIQUE_TYPE_COLNAME,
            TRANSITIVE_TRACE_TYPE_COLNAME,
        ]
        rank_groups_in_data = [col for col in rank_groups if col in self.table.columns]

        for _, values in data.groupby(rank_groups_in_data):
            values[new_col_name] = values[rank_col].rank(
                method="dense", ascending=False
            )
            if aggregated_rank_df is None:
                aggregated_rank_df = values
            else:
                aggregated_rank_df = pd.concat(
                    [aggregated_rank_df, values], ignore_index=True
                )
        return MetricTable(aggregated_rank_df)

    def calculate_gain(
        self, base_indices: List[int], target_indices: List[int]
    ) -> Table:
        """
        Given two list of equally sized indices, looks up each index pair in table and calculates the gain for each
        metric where inversions are accounted for.
        :param base_indices: indices in the table corresponding to the baseline techniques
        :param target_indices: indices corresponding to the target techniques whose gain we are interested
        :return: Equally sized DataFrame containing the gain value for each metric found in table.
        """
        assert len(base_indices) == len(
            target_indices
        ), "expected base and target indices to have same size"

        base_metrics = (
            self.table.iloc[base_indices][[DATASET_COLNAME] + CORE_METRIC_NAMES]
            .sort_values(by=DATASET_COLNAME)
            .reset_index(drop=True)
        )
        target_metrics = (
            self.table.iloc[target_indices][[DATASET_COLNAME] + CORE_METRIC_NAMES]
            .sort_values(by=DATASET_COLNAME)
            .reset_index(drop=True)
        )

        dataset_order = base_metrics[DATASET_COLNAME]
        gain_values = calculate_gain_between_techniques(
            base_metrics.drop(DATASET_COLNAME, axis=1),
            target_metrics.drop(DATASET_COLNAME, axis=1),
        )
        gain_values[DATASET_COLNAME] = dataset_order

        return MetricTable(gain_values).melt_metrics(
            metric_value_col_name=RELATIVE_GAIN_COLNAME
        )

    def calculate_percent_best(self) -> Table:
        """
        For each transitive trace type and variation point, calculates the percent of times it had a rank of 1 across
        all datasets. Missing groups columns are ignored.
        :return:
        """
        data = self.create_ranks().table.copy()

        # 1. extract variation points (e.g. AlgebraicModel, TraceType, ect.)
        non_vp_columns = (
            ALL_METRIC_NAMES
            + META_COLS
            + [RANK_COLNAME, TECHNIQUE_TYPE_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME]
        )
        vp_cols = [col for col in data.columns if col not in non_vp_columns]

        percent_best_df = pd.DataFrame()
        n_datasets = (
            len(data[DATASET_COLNAME].unique())
            if DATASET_COLNAME in data.columns
            else 1
        )

        group_by_cols_in_dataset = [
            col
            for col in [
                TRANSITIVE_TRACE_TYPE_COLNAME,
                TECHNIQUE_TYPE_COLNAME,
            ]
            if col in data.columns
        ]

        for variation_point in vp_cols:
            for group_id, group_data in data.groupby(
                [variation_point] + group_by_cols_in_dataset
            ):
                best_rank_query = group_data[group_data[RANK_COLNAME] == 1]
                n_datasets_in_query = (
                    1
                    if DATASET_COLNAME not in best_rank_query.columns
                    else len(best_rank_query[DATASET_COLNAME].unique())
                )
                vp_freq = n_datasets_in_query / n_datasets
                new_record = {
                    VARIATION_POINT_COLNAME: variation_point,
                    TECHNIQUE_COLNAME: group_id[0],
                    PERCENT_BEST_COLNAME: vp_freq,
                }

                if len(group_id) >= 2:
                    new_record.update({TRANSITIVE_TRACE_TYPE_COLNAME: group_id[1]})

                if len(group_id) >= 3:
                    new_record.update({TECHNIQUE_TYPE_COLNAME: group_id[2]})

                percent_best_df = percent_best_df.append(new_record, ignore_index=True)

        return Table(percent_best_df)

    def create_correlation_table(self) -> "Table":
        """
        :return: Table containing columns describing the correlation and p-value for each dataset-metric combination.
        """
        data = self.table.copy()
        correlation_df = pd.DataFrame()
        metrics = data[METRIC_COLNAME].unique()
        datasets = data[DATASET_COLNAME].unique()

        queryable = data.set_index([DATASET_COLNAME, METRIC_COLNAME])
        for dataset_name in datasets:
            for metric_name in metrics:
                query = queryable.loc[dataset_name, metric_name]

                metric_values: List[float] = list(query["value"])
                percent_values: List[float] = list(query["percent"])

                correlation, p_value = spearmanr(metric_values, percent_values)
                correlation = (
                    -1 * correlation if metric_name in INVERTED_METRICS else correlation
                )
                correlation_df = correlation_df.append(
                    {
                        DATASET_COLNAME: dataset_name,
                        METRIC_COLNAME: metric_name.lower(),
                        CORRELATION_COLNAME: round(correlation, N_SIG_FIGS),
                        P_VALUE_COLNAME: "<0.001"
                        if p_value < 0.001
                        else str(round(p_value, N_SIG_FIGS)),
                    },
                    ignore_index=True,
                )
        return Table(correlation_df)

    def melt_metrics(
        self, metric_col_name=METRIC_COLNAME, metric_value_col_name="value"
    ) -> Table:
        """
        Converts each metric column in table into a row-entry containing all identifying information
        (taken to be all non-metric columns) and the metric score
        :return: Table - containing metric row-entries alongside the identifying information
        """
        metric_found = [
            metric for metric in ALL_METRIC_NAMES if metric in self.table.columns
        ]
        other_columns = [col for col in self.table.columns if col not in metric_found]
        melted_df = pd.melt(
            self.table,
            id_vars=other_columns,
            value_vars=metric_found,
            var_name=metric_col_name,
            value_name=metric_value_col_name,
        )
        return Table(melted_df)

    # pylint: disable=too-many-arguments
    def scale_col(
        self,
        col_name: str,
        group_by_cols: [str],
        new_col_name=None,
        drop_old=False,
        inverted=False,
    ) -> Table:
        """
        Performs min-max scaling on given column name, renames new values to scaled_col_name.
        If none is given appends `normalized` to metric_name
        :param col_name: the name of the metric in the table to scale
        :param group_by_cols: list of col name to group by before scaling
        :param new_col_name: name of the column containing scaled values
        :param drop_old: if true removes the column without the scaled numbers
        :param inverted: metrics scores will be inverted so that new_score = 1 - old_score
        :return: None - MetricTable is modified
        TODO: Separate into multiple functionality and remove linting bypass
        """
        new_col_name = (
            new_col_name
            if new_col_name is not None
            else "%s_%s" % (col_name, "normalized")
        )
        sections = self.table.groupby(group_by_cols).groups
        new_sections = []
        for _, group_indices in sections.items():
            dataset_df = self.table.iloc[group_indices].copy()
            dataset_df[new_col_name] = minmax_scale(dataset_df[col_name])
            new_sections.append(dataset_df)

        agg_df = pd.concat(new_sections, axis=0)

        if inverted:
            inverted_col_name = "%s_%s" % (new_col_name, "inverted")
            agg_df[inverted_col_name] = 1 - agg_df[new_col_name]

        if drop_old:
            agg_df = agg_df.drop(col_name, axis=1)
            if inverted:
                agg_df = agg_df.drop(new_col_name, axis=1)

        return Table(agg_df)

    def create_lag_norm_inverted(
        self, remove_old_lag=True, new_metric_name=LAG_NORMALIZED_INVERTED_COLNAME
    ) -> "MetricTable":
        """
        For each dataset in table, Lag is normalized to be between [0,1] and then inverted so that an increase in score
        correlates with an increase in accuracy. New metric is stored in a new column with the specified name.
        :param remove_old_lag: boolean - whether to remove original lag metric
        :param new_metric_name: str - what to call the new metric.
        :return: MetricTable - contains the new metric
        """
        data = self.table.copy()
        datasets = data[DATASET_COLNAME].unique()

        intermediate_data = []
        for dataset in datasets:
            dataset_query = data[data[DATASET_COLNAME] == dataset].copy()
            dataset_query[new_metric_name] = 1 - minmax_scale(
                list(dataset_query[LAG_COLNAME])
            )
            intermediate_data.append(dataset_query)

        data = pd.concat(intermediate_data).reset_index(drop=True)
        if remove_old_lag:
            data = data.drop(LAG_COLNAME, axis=1)
        return MetricTable(data)

    def metrics_to_upper_case(self):
        """
        Converts all metric values into upper case representation
        :return: MetricTable with metric values in upper case
        """
        data = self.table.copy()
        data[METRIC_COLNAME] = data[METRIC_COLNAME].apply(lambda m: m.upper())
        return MetricTable(data)

    def calculate_gain_between(
        self, source_col: str, base_col: str, gain_col_name: str
    ) -> "MetricTable":
        """
        Calculates the relative gain between source score and target score
        :param source_col: the columns being compared
        :param base_col: the values being compare to
        :param gain_col_name: name of column containing relative gain scores
        :return:
        """
        is_inverted: bool = source_col in INVERTED_METRICS
        data = self.table.copy()
        if is_inverted:
            data[gain_col_name] = (data[base_col] - data[source_col]) / data[base_col]
        else:
            data[gain_col_name] = (data[source_col] - data[base_col]) / data[base_col]
        return MetricTable(data)


class Metrics:  # pylint: disable=too-few-public-methods
    """
    Stores all metrics for some query.
    TODO: Convert to named tuple
    """

    def __init__(self, ap: float, auc: float, lag: float):
        self.ap = ap  # pylint: disable=invalid-name
        self.auc = auc
        self.lag = lag

    def gain(self, base: "Metrics"):
        """
        Calculates the gain of these metrics to given base metrics
        :param base: base metrics to use for comparison
        :return:
        """
        ap_gain = (self.ap - base.ap) / base.ap
        auc_gain = (self.auc - base.auc) / base.auc
        lag_gain = (base.lag - self.lag) / base.lag if base.lag != 0 else None
        return Metrics(ap_gain, auc_gain, lag_gain)


def calculate_gain_between_techniques(base_metrics: Data, target_metrics: Data) -> Data:
    """
    Given two DataFrames of metrics, calculates gain per row per metrics
    Returns a DataFrame containing the gain of each row in t2 with its corresponding row and metric in t1
    :param base_metrics: the base values which to calculate gain from
    :param target_metrics: the target values whose gain we are examining
    :return: DataFrame containing metrics as columns as a row for every row in base_metrics/target_metrics
    """
    assert len(base_metrics) == len(target_metrics), "results do not have same size"
    gain_df = pd.DataFrame()
    for i in range(len(base_metrics)):
        entry = {}
        for metric in base_metrics.columns:
            base_score = base_metrics.iloc[i][metric]
            target_score = target_metrics.iloc[i][metric]
            is_inverted = metric in INVERTED_METRICS
            gain = calculate_gain(base_score, target_score, inverted=is_inverted)
            entry.update({metric: gain})
        gain_df = gain_df.append(entry, ignore_index=True)
    return gain_df


def calculate_gain(base_value: float, new_value: float, inverted=False):
    """
    Calculates the gain between new_value and old_value, where the percentage returned is how much new_value improved
    over old_value. If inverted = True then returns percentage of how much LESS new_value is than old_value
    :param new_value: : float - the value that is being compared to the base value
    :param base_value: float - the base value serving as the comparison pillar
    :param inverted: whether to return how much new_value is less than base_value
    :return:
    """
    if inverted:
        return (base_value - new_value) / base_value
    return (new_value - base_value) / base_value


def get_best_rows(data: Data, metric_name: str):
    """
    Returns copy of data containing only the rows with the highest score for given metric
    :param data: DataFrame - containing metric column
    :param metric_name: the metric used to decide which row is "best"
    :return: DataFrame
    """
    data = data.copy()
    return data[
        data.groupby([DATASET_COLNAME])[metric_name].transform(max) == data[metric_name]
    ]
