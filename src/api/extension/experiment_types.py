"""
The following module contains the custom classes used during the experiments of LeveragingIntermediateArtifacts.
"""
from enum import Enum


class ExperimentTraceType(Enum):
    """
    Depicts the different modes of utilizing transitive traces.
    """

    DIRECT = "direct"
    NONE = "none"
    UPPER = "upper"
    LOWER = "lower"
    ALL = "all"


class SamplingExperiment(Enum):
    """
    Represents the different types of sampling that can be performed.
    """

    TRACES = "traces"
    ARTIFACTS = "artifacts"
