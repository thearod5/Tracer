"""
This module stores the constants regarding the names of columns for any pre or post processing operations.
"""
import pandas as pd

from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.extension.experiment_types import ExperimentTraceType, SamplingExperiment

N_SIG_FIGS = 3

DATASET_COLNAME = "dataset"
NAME_COLNAME = "name"

SCORE_COLNAME = "score"
METRIC_COLNAME = "metric"
METRIC_SCORE_COLNAME = "metric_score"
QUERY_INDEX_COLNAME = "query_index"
AP_COLNAME = "ap"
AUC_COLNAME = "auc"
LAG_COLNAME = "lag"
CORE_METRIC_NAMES = [AP_COLNAME, AUC_COLNAME, LAG_COLNAME]
LAG_NORMALIZED_COLNAME = "lag_normalized"
LAG_NORMALIZED_INVERTED_COLNAME = "lag_normalized_inverted"
ALL_METRIC_NAMES = CORE_METRIC_NAMES + [
    LAG_NORMALIZED_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
]
BEST_TECHNIQUE_AGGREGATE_METRICS = [
    AP_COLNAME,
    AUC_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
]
INVERTED_METRICS = [LAG_COLNAME, LAG_NORMALIZED_COLNAME]
DIRECT_ALGEBRAIC_MODEL_COLNAME = "direct_algebraic_model"
TRANSITIVE_ALGEBRAIC_MODEL_COLNAME = "transitive_algebraic_model"
TRANSITIVE_SCALING_COLNAME = "transitive_scaling"
TRANSITIVE_AGGREGATION_COLNAME = "transitive_aggregation"
TECHNIQUE_AGGREGATION_COLNAME = "technique_aggregation"
TRANSITIVE_TRACE_TYPE_COLNAME = "transitive_trace_type"
TECHNIQUE_TYPE_COLNAME = "technique_type"
TECHNIQUE_TYPE_SORT_ORDER = [DIRECT_ID, TRANSITIVE_ID, HYBRID_ID]

VARIATION_POINT_COLNAME = "variation_point"
RELATIVE_GAIN_COLNAME = "relative_gain"
TECHNIQUE_COLNAME = "technique"
RANK_COLNAME = "map_rank"
PERCENT_BEST_COLNAME = "percent_best"

PERCENT_COLNAME = "percent"
VALUE_COLNAME = "value"
CORRELATION_COLNAME = "correlation"
P_VALUE_COLNAME = "p_value"

META_COLS = [DATASET_COLNAME, NAME_COLNAME]
TECHNIQUE_COLS = [
    DIRECT_ALGEBRAIC_MODEL_COLNAME,
    TRANSITIVE_ALGEBRAIC_MODEL_COLNAME,
    TRANSITIVE_SCALING_COLNAME,
    TRANSITIVE_AGGREGATION_COLNAME,
    TECHNIQUE_AGGREGATION_COLNAME,
]
PERCENT_BEST_SORT_ORDER = [
    VARIATION_POINT_COLNAME,
    TECHNIQUE_COLNAME,
    PERCENT_BEST_COLNAME,
]
CORRELATION_COL_ORDER = [RELATIVE_GAIN_COLNAME, CORRELATION_COLNAME, P_VALUE_COLNAME]
COLUMN_ORDER = (
    [
        DATASET_COLNAME,
        TECHNIQUE_TYPE_COLNAME,
        TRANSITIVE_TRACE_TYPE_COLNAME,
        QUERY_INDEX_COLNAME,
        METRIC_COLNAME,
    ]
    + TECHNIQUE_COLS
    + ALL_METRIC_NAMES
    + PERCENT_BEST_SORT_ORDER
    + CORRELATION_COL_ORDER
    + [NAME_COLNAME]
)

TRANSITIVE_TRACE_TYPE_ORDER = [tt.value for tt in ExperimentTraceType]
Data = pd.DataFrame
Scores = pd.Series
MeltedData = pd.DataFrame
DF_METRICS = [AP_COLNAME, AUC_COLNAME, LAG_COLNAME, LAG_NORMALIZED_INVERTED_COLNAME]
SAMPLING_METHODS = [et.value for et in SamplingExperiment]

MinAccuracyTable = Data
MedianAccuracyTable = Data
MaxAccuracyTable = Data
