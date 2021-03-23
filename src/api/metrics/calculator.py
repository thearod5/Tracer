"""
TODO
"""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_curve, auc

from api.constants.processing import CORE_METRIC_NAMES
from api.tables.metric_table import Metrics
from api.tables.scoring_table import ScoringTable

SINGLE_QUERY_METRIC_TABLE_COLUMNS = ["dataset", "type"] + CORE_METRIC_NAMES


def calculate_auc(y_true, y_pred):
    """
    TODO
    :param y_true:
    :param y_pred:
    :return:
    """
    fpr, tpr, _ = roc_curve(y_true, y_pred, pos_label=1)
    return auc(fpr, tpr)


def number_of_fp_above_index(sorted_y_true, index):
    """
    TODO
    :param sorted_y_true:
    :param index:
    :return:
    """
    elements_above = list(sorted_y_true[:index])
    if len(elements_above) == 0:
        return 0
    return elements_above.count(0)


def calculate_lag(y_true, y_pred):
    """
    TODO
    :param y_true:
    :param y_pred:
    :return:
    """
    y_pred_series = pd.Series(y_pred)
    sorted_index = list(y_pred_series.sort_values(ascending=False).index)
    y_true_sorted = pd.Series(y_true)[sorted_index].reset_index(drop=True)

    lags = []
    prev_lag = 0
    for _, value in enumerate(y_true_sorted):
        if value == 0:
            prev_lag = prev_lag + 1
        else:
            lags.append(prev_lag)
    if len(lags) == 0:
        return 0
    return np.mean(lags)


def calculate_ap(y_true, y_pred):
    """
    Returns the AP scores for given query.
    :param y_true: flattened oracle values
    :param y_pred: flattened predicted values
    :return AP score
    """
    return average_precision_score(y_true=y_true, y_score=y_pred)


def calculate_metrics_for_scoring_table(
        scoring_table: ScoringTable, n_queries: int
) -> [Metrics]:
    """
    Returns list of Metrics per query in scoring table
    :param scoring_table: contains flattened list of predicted and oracle values
    :param n_queries: number of queries in scoring table, table length must be divisible by n_queries
    :return: Metrics corresponding 1-1 with query indices in scoring table
    """
    y_pred = scoring_table.values[:, 0]
    y_true = scoring_table.values[:, 1]

    assert (
            len(y_true) % n_queries == 0
    ), "given number of queries (%d) does not divide into values (%d)" % (
        n_queries,
        len(y_true),
    )
    query_length = int(len(y_true) / n_queries)
    assert query_length != 0, "length of y true %d" % len(y_true)
    m_entries = []

    for query_index in range(n_queries):
        start_i = query_index * query_length
        end_i = start_i + query_length
        query_y_pred = y_pred[start_i:end_i]
        query_length = len(query_y_pred)
        start_index = query_index * query_length
        end_index = start_index + query_length
        query_y_true = y_true[start_index:end_index]

        m_entry = Metrics(
            ap=calculate_ap(query_y_true, query_y_pred),
            auc=calculate_auc(query_y_true, query_y_pred),
            lag=calculate_lag(query_y_true, query_y_pred),
        )

        m_entries.append(m_entry)
    return m_entries
