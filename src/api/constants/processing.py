"""
This module stores the constants regarding the names of columns for any pre or post processing operations.
"""
import pandas as pd

N_SIG_FIGS = 3

DATASET_COLNAME = "dataset"
NAME_COLNAME = "name"

SCORE_COLNAME = "score"
METRIC_COLNAME = "metric"
QUERY_INDEX_COLNAME = "query_index"
AP_COLNAME = "ap"
AUC_COLNAME = "auc"
LAG_COLNAME = "lag"
CORE_METRIC_NAMES = [AP_COLNAME, AUC_COLNAME, LAG_COLNAME]
LAG_NORMALIZED_COLNAME = "lag_normalized"
LAG_NORMALIZED_INVERTED_COLNAME = "lag_normalized_inverted"
ALL_METRIC_NAMES = [AP_COLNAME, AUC_COLNAME, LAG_COLNAME, LAG_NORMALIZED_COLNAME, LAG_NORMALIZED_INVERTED_COLNAME]

DIRECT_ALGEBRAIC_MODEL_COLNAME = "direct_algebraic_model"
ALGEBRAIC_MODEL_COLNAME = "transitive_algebraic_model"
TRANSITIVE_SCALING_COLNAME = "transitive_scaling"
TRANSITIVE_AGGREGATION_COLNAME = "transitive_aggregation"
TECHNIQUE_AGGREGATION_COLNAME = "technique_aggregation"
TRANSITIVE_TRACE_TYPE_COLNAME = "transitive_trace_type"
TECHNIQUE_TYPE_COLNAME = "technique_type"

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
TECHNIQUE_COLS = [DIRECT_ALGEBRAIC_MODEL_COLNAME,
                  ALGEBRAIC_MODEL_COLNAME,
                  TRANSITIVE_SCALING_COLNAME,
                  TRANSITIVE_AGGREGATION_COLNAME,
                  TECHNIQUE_AGGREGATION_COLNAME]
COLUMN_ORDER = [DATASET_COLNAME, TECHNIQUE_TYPE_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME] + TECHNIQUE_COLS + [
    NAME_COLNAME] + ALL_METRIC_NAMES
DATASET_COLUMN_ORDER = ["WARC", "Drone", "EasyClinic", "TrainController", "EBT"]
Data = pd.DataFrame
Scores = pd.Series
MeltedData = pd.DataFrame
DF_METRICS = [AP_COLNAME, AUC_COLNAME, LAG_COLNAME, LAG_NORMALIZED_INVERTED_COLNAME]

MinAccuracyTable = Data
MedianAccuracyTable = Data
MaxAccuracyTable = Data
