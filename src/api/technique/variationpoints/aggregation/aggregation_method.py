"""
TODO
"""
from enum import Enum


class AggregationMethod(Enum):
    """
    The methods in which a series of numbers is combined into one.

    There are two scenarios in which this step is necessary:
    1. Aggregating transitive relation scores between a source and target artifacts into a single score
    2. Aggregation two (or more) techniques into a single technique represented as a similarity matrix.
    """
    PCA = "PCA"
    SUM = "SUM"
    MAX = "MAX"
