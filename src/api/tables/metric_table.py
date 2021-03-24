"""
This module is responsible to creating a proxy-class encapsulating all pre/post-processing operations defined
on a metric table.
"""

import itertools
from typing import Optional

import pandas as pd
from sklearn.preprocessing import minmax_scale

from api.constants.processing import (
    ALL_METRIC_NAMES,
    AP_COLNAME,
    DATASET_COLNAME,
    Data,
    INVERTED_METRICS,
    LAG_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
    META_COLS,
    METRIC_COLNAME,
    N_SIG_FIGS,
    PERCENT_BEST_COLNAME,
    RANK_COLNAME,
    RELATIVE_GAIN_COLNAME,
    Scores,
    TECHNIQUE_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
    VALUE_COLNAME,
    VARIATION_POINT_COLNAME,
)
from api.extension.experiment_types import ExperimentTraceType
from api.tables.table import Table


class MetricTable(Table):
    """
    Represents a table containing technique identification information and metric scores
    """

    def __init__(
        self, table: Optional[Data] = None, path_to_table: Optional[str] = None
    ):
        super().__init__(table, path_to_table=path_to_table)

    def create_ranks(self, rank_col=AP_COLNAME, new_col_name=RANK_COLNAME) -> Table:
        """
        For each dataset and trace type, create ranks with 1 corresponding to highest map score
        :param rank_col: str - the name of the column to be used for ranking
        :param new_col_name: str - the name of the new column containing the ranks
        :return:
        """
        data = self.table.copy()
        aggregated_rank_df = None

        rank_groups = [DATASET_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME]
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
        return Table(aggregated_rank_df)

    def calculate_gain(self) -> Table:  # pylint: disable=too-many-locals
        """
        TODO: Docs
        TODO: too many local vars
        :return:
        """
        id_columns = [DATASET_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME]
        ids_unique_values = [list(self.table[col].unique()) for col in id_columns]

        melted_df = MetricTable(self.table).create_melted_metrics().table
        metrics = melted_df[METRIC_COLNAME].unique()

        result = pd.DataFrame(
            columns=id_columns + [METRIC_COLNAME, RELATIVE_GAIN_COLNAME]
        )
        for dataset, trace_type, metric_name in itertools.product(
            ids_unique_values[0], ids_unique_values[1], metrics
        ):
            dataset_metric_query = melted_df[
                (melted_df[DATASET_COLNAME] == dataset)
                & (melted_df[METRIC_COLNAME] == metric_name)
            ]
            baseline_values = dataset_metric_query[
                dataset_metric_query[TRANSITIVE_TRACE_TYPE_COLNAME]
                == ExperimentTraceType.DIRECT.value
            ][VALUE_COLNAME]
            query_df = dataset_metric_query[
                dataset_metric_query[TRANSITIVE_TRACE_TYPE_COLNAME] == trace_type
            ]

            is_inverted = metric_name in INVERTED_METRICS
            baseline_value = (
                min(baseline_values) if is_inverted else max(baseline_values)
            )
            experiment_value = query_df[VALUE_COLNAME]
            gain_values = calculate_gain_for_scores(
                experiment_value, baseline_value, is_inverted
            )

            assert len(gain_values) > 0
            max_gain = round(max(gain_values), N_SIG_FIGS)
            result = result.append(
                {
                    DATASET_COLNAME: dataset,
                    TRANSITIVE_TRACE_TYPE_COLNAME: trace_type,
                    METRIC_COLNAME: metric_name,
                    RELATIVE_GAIN_COLNAME: max_gain,
                },
                ignore_index=True,
            )
        return Table(result)

    def calculate_percent_best(self) -> Table:
        """
        For each transitive trace type and variation point, calculates the percent of times it had a rank of 1 across
        all datasets. Missing groups columns are ignored.
        :return:
        """
        data = self.create_ranks().table.copy()

        # 1. extract variation points (e.g. AlgebraicModel, TraceType, ect.)
        non_vp_columns = (
            ALL_METRIC_NAMES + META_COLS + [RANK_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME]
        )
        vp_cols = [col for col in data.columns if col not in non_vp_columns]

        percent_best_df = pd.DataFrame()
        n_datasets = (
            len(data[DATASET_COLNAME].unique())
            if DATASET_COLNAME in data.columns
            else 1
        )

        for variation_point in vp_cols:
            for (trace_type, vp_technique), group_data in data.groupby(
                [TRANSITIVE_TRACE_TYPE_COLNAME, variation_point]
            ):
                best_rank_query = group_data[group_data[RANK_COLNAME] == 1]
                n_datasets_in_query = (
                    1
                    if DATASET_COLNAME not in best_rank_query.columns
                    else len(best_rank_query[DATASET_COLNAME].unique())
                )
                vp_freq = n_datasets_in_query / n_datasets
                new_record = {
                    TRANSITIVE_TRACE_TYPE_COLNAME: trace_type,
                    VARIATION_POINT_COLNAME: variation_point,
                    TECHNIQUE_COLNAME: vp_technique,
                    PERCENT_BEST_COLNAME: vp_freq,
                }
                percent_best_df = percent_best_df.append(new_record, ignore_index=True)

        return Table(percent_best_df).sort_cols()

    def create_melted_metrics(
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
        Creates a new metric, lag normalized and inverted, where the lag scores are first scaled to be between 0 and 1
        then they are inverted so that 1 means an accurate score and 0 an inaccurate one. This new metric is stored in
        a new column with the specified name.
        :param remove_old_lag: boolean - whether to remove original lag metric
        :param new_metric_name: str - what to call the new metric.
        :return: MetricTable - contains the new metric
        """
        data = self.table.copy()
        data[new_metric_name] = 1 - minmax_scale(list(data[LAG_COLNAME]))
        if remove_old_lag:
            data = data.drop(LAG_COLNAME, axis=1)
        return MetricTable(data)

    def setup_for_graph(self) -> Table:
        """
        Normalized and inverts lag, melts the metrics, and formats the table for display.
        :return: Table - a copy of this table but with the processing steps above.
        """
        return (
            self.create_lag_norm_inverted(True).create_melted_metrics().format_table()
        )


class Metrics:  # pylint: disable=too-few-public-methods
    """
    Stores all metrics for some query.
    TODO: Convert to named tuple
    """

    def __init__(self, ap: float, auc: float, lag: float):
        self.ap = ap  # pylint: disable=invalid-name
        self.auc = auc
        self.lag = lag


def calculate_gain(new_value: float, base_value: float, inverted=False):
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


def calculate_gain_for_scores(scores: Scores, base_value: float, inverted: bool):
    """
    Calculates the gain for each score according to given base_value
    :param scores:
    :param base_value:
    :param inverted:
    :return:
    """
    return scores.apply(lambda score: calculate_gain(score, base_value, inverted))
