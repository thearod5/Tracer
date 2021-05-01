"""
This module is responsible to creating a proxy-class encapsulating all pre/post-processing operations defined
on a metric table.
"""

from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from scipy.stats import spearmanr
from sklearn.preprocessing import minmax_scale, scale

from api.constants.processing import (
    ALL_METRIC_NAMES,
    AP_COLNAME,
    BEST_TECHNIQUE_AGGREGATE_METRICS,
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

    def find_best_direct_techniques(self) -> "MetricTable":
        """
        Finds the highest performing direct techniques in table containing dataset
        name and technique type identifiers
        :return: Table
        """
        data = self.table.copy()
        direct_mask = self.get_technique_type_mask(DIRECT_ID)
        return find_best_techniques(data[direct_mask])

    def find_best_transitive_techniques(self) -> "MetricTable":
        """
        Finds the transitive techniques that performed the best on given metric table.
        Note, only techniques without transitive traces are considered.
        :return: Table
        """
        data = self.table.copy()
        query_mask = self.get_none_traced_mask() & self.get_technique_type_mask(
            TRANSITIVE_ID
        )

        return find_best_techniques(data[query_mask])

    def find_best_hybrid_techniques(self) -> "MetricTable":
        """
        Returns the set of indices corresponding to the best combined, non-traced techniques.
        :return: Table
        """

        data = self.table.copy()
        query_mask = self.get_none_traced_mask() & self.get_technique_type_mask(
            HYBRID_ID
        )
        return find_best_techniques(data[query_mask])

    def find_worst_direct_techniques(self) -> "MetricTable":
        """
        Fins the highest performing direct techniques
        :return: Table
        """
        data = self.table.copy()
        direct_mask = self.get_technique_type_mask(DIRECT_ID)
        return find_worst_techniques(data[direct_mask])

    def find_worst_transitive_techniques(self) -> "MetricTable":
        """
        Finds the transitive techniques that performed the best on given metric table.
        Note, only techniques without transitive traces are considered.
        :return: Table
        """
        data = self.table.copy()
        query_mask = self.get_none_traced_mask() & self.get_technique_type_mask(
            TRANSITIVE_ID
        )

        return find_worst_techniques(data[query_mask])

    def find_worst_hybrid_techniques(self) -> "MetricTable":
        """
        Returns the set of indices corresponding to the best combined, non-traced techniques.
        :return: Table
        """

        data = self.table.copy()
        query_mask = self.get_none_traced_mask() & self.get_technique_type_mask(
            HYBRID_ID
        )
        return find_worst_techniques(data[query_mask])

    def get_best_combined_no_traces_indices(self) -> List[int]:
        """
        Returns the set of indices corresponding to the best combined, non-traced techniques.
        """

        return self.find_best_hybrid_techniques().table.index

    def get_technique_indices(self, technique_definition: str) -> List[int]:
        """
        Calculates the gain between given technique and direct best
        :param technique_definition:
        :return:
        """
        return self.table[self.table[NAME_COLNAME] == technique_definition].index

    def get_none_traced_mask(self) -> Union[bool, List[bool]]:
        """
        Returns boolean mask for all rows whose trace type is NONE (e.g. uses no transitive traces).
        If columns does not exist than table is assumed to be traced.
        :return: boolean mask
        """
        if TRANSITIVE_TRACE_TYPE_COLNAME not in self.table.columns:
            return [True] * len(self.table)
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
        gain_values = calculate_gain_between_metrics(
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

    def create_lag_norm_inverted(
        self, drop_old=True, new_metric_name=LAG_NORMALIZED_INVERTED_COLNAME
    ) -> "MetricTable":
        """
        For each dataset in table, Lag is normalized to be between [0,1] and then inverted so that an increase in score
        correlates with an increase in accuracy. New metric is stored in a new column with the specified name.
        :param drop_old: boolean - whether to remove original lag metric
        :param new_metric_name: str - what to call the new metric.
        :return: MetricTable - contains the new metric
        """
        data = self.table.copy()
        datasets = data[DATASET_COLNAME].unique()

        intermediate_data = [] if len(datasets) > 0 else data
        for dataset in datasets:
            dataset_query = data[data[DATASET_COLNAME] == dataset].copy()
            dataset_query[new_metric_name] = 1 - minmax_scale(
                list(dataset_query[LAG_COLNAME])
            )
            intermediate_data.append(dataset_query)

        data = pd.concat(intermediate_data).reset_index(drop=True)
        if drop_old:
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

    def calculate_gain_between_techniques(
        self, dataset_comparison: Dict[str, Tuple[str, str]]
    ) -> "MetricTable":
        """
        Calculates the relative gain each tuple in the value of each key.
        :param dataset_comparison: Dictionary containing dataset names as keys and the
        names of the techniques to compare in a tuple
        :return:
        """
        data = self.table.copy()
        aggregate = None
        for dataset, techniques_to_compare in dataset_comparison.items():
            base_technique = techniques_to_compare[0]
            target_technique = techniques_to_compare[1]
            base_technique_query = data[
                (data[DATASET_COLNAME] == dataset)
                & (data[NAME_COLNAME] == base_technique)
            ]
            target_technique_query = data[
                (data[DATASET_COLNAME] == dataset)
                & (data[NAME_COLNAME] == target_technique)
            ]

            assert (
                len(base_technique_query) == 1 and len(target_technique_query) == 1
            ), f"{dataset}:{len(base_technique_query)}:{len(target_technique_query)}"

            gain_in_metrics = calculate_gain_between_metrics(
                base_technique_query, target_technique_query
            )

            gain_in_metrics[DATASET_COLNAME] = dataset

            aggregate = (
                gain_in_metrics
                if aggregate is None
                else pd.concat([gain_in_metrics, aggregate])
            )

        return MetricTable(aggregate)


class Metrics:  # pylint: disable=too-few-public-methods
    """
    Stores all metrics for some query.
    TODO: Convert to named tuple
    """

    def __init__(self, ap: float, auc: float, lag: float, query_id: int = 0):
        self.query_id = query_id
        self.ap = ap  # pylint: disable=invalid-name
        self.auc = auc
        self.lag = lag


def calculate_gain_between_metrics(base_metrics: Data, target_metrics: Data) -> Data:
    """
    Given two DataFrames of metrics, calculates gain per row per metrics
    Returns a DataFrame containing the gain of each row in t2 with its corresponding row and metric in t1
    :param base_metrics: the base values which to calculate gain from
    :param target_metrics: the target values whose gain we are examining
    :return: DataFrame containing metrics as columns as a row for every row in base_metrics/target_metrics
    """
    assert len(base_metrics) == len(target_metrics), "results do not have same size"
    gain_df = pd.DataFrame()
    metrics = list(filter(lambda c: c in ALL_METRIC_NAMES, base_metrics.columns))
    for i in range(len(base_metrics)):
        entry = {}
        for metric in metrics:
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
    assert isinstance(base_value, (int, float))
    assert isinstance(new_value, (int, float))

    base_value = 1.0 * base_value
    new_value = 1.0 * new_value
    if inverted:
        return (base_value - new_value) / base_value * 1.0
    return (new_value - base_value) / base_value * 1.0


AGGREGATE_METRIC_COLNAME = (
    "aggregate_metric"  # the metric used to determine the best techniques.
)


def process_for_best_technique_evaluation(data: Data):
    """
    Creates the necessary normalized metrics (e.g. for lag) to be able to compare
    rows.
    :param data:
    :return:
    """
    metric_table = MetricTable(data)
    data = (
        data
        if LAG_NORMALIZED_INVERTED_COLNAME in data
        else metric_table.create_lag_norm_inverted().table
    )
    return data


def find_best_techniques(data: Data):
    """
    Returns rows in data containing highest sum of map, auc, and lag_normalized_inverted (after standardization).
    :param data: DataFrame containing columns: map, auc, and lag_normalized_inverted
    :return:  Subset DataFrame of given Data
    """
    data = data.copy()
    data = process_for_best_technique_evaluation(data)
    best_techniques_df = get_best_rows(
        data,
        BEST_TECHNIQUE_AGGREGATE_METRICS,
    )
    return MetricTable(best_techniques_df)


def find_worst_techniques(data: Data):
    """
    Returns rows in data containing lowest sum of map, auc, and lag_normalized_inverted (after standardization).
    :param data: DataFrame containing columns: map, auc, and lag_normalized_inverted
    :return: Subset DataFrame of given Data
    """
    data = data.copy()
    data = process_for_best_technique_evaluation(data)
    best_techniques_df = get_worst_rows(
        data,
        BEST_TECHNIQUE_AGGREGATE_METRICS,
    )
    return MetricTable(best_techniques_df)


def get_best_rows(data: Data, metrics: List[str]):
    """
    Returns copy of data containing only the rows with the highest score for given metric
    :param data: DataFrame - containing metric column
    :param metrics: the metric used to decide which row is "best"
    :return: DataFrame
    """
    return query_agg_metric(data, metrics, max)


def get_worst_rows(data: Data, metric_names: List[str]):
    """
    Returns copy of data containing only the rows with the highest score for given metric
    :param data: DataFrame - containing metric column
    :param metric_names: the metric used to decide which row is "best"
    :return: DataFrame
    """
    return query_agg_metric(data, metric_names, min)


def query_agg_metric(data: Data, metric_names: List[str], agg_func):
    """
    Returns copy of data containing only the rows with the highest score for given metric
    :param data: DataFrame - containing metric column
    :param metric_names: the metric used to decide which row is "best"
    :param agg_func:
    :param scale_func:
    :return: DataFrame
    """
    data = data.copy()

    aggregate_metric_values = None
    for metric in metric_names:
        aggregate_metric_values = (
            scale(data[metric])
            if aggregate_metric_values is None
            else aggregate_metric_values + scale(data[metric])
        )
    data[AGGREGATE_METRIC_COLNAME] = aggregate_metric_values
    query = data[
        data.groupby([DATASET_COLNAME])[AGGREGATE_METRIC_COLNAME].transform(agg_func)
        == data[AGGREGATE_METRIC_COLNAME]
    ]
    return query.drop(AGGREGATE_METRIC_COLNAME, axis=1)
