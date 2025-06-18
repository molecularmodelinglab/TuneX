from enum import Enum


class TargetMode(Enum):
    MIN = "Min"
    MAX = "Max"
    MATCH = "Match"


class ParameterType(Enum):
    """Parameter types for campaign optimization."""

    DISCRETE_NUMERICAL_REGULAR = "discrete_numerical_regular"
    DISCRETE_NUMERICAL_IRREGULAR = "discrete_numerical_irregular"
    CONTINUOUS_NUMERICAL = "continuous_numerical"
    CATEGORICAL = "categorical"
    FIXED = "fixed"
    SUBSTANCE = "substance"
