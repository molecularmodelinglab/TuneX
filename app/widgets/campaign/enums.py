# campaign/enums.py
from enum import Enum

class TargetMode(Enum):
    MIN = "Min"
    MAX = "Max"
    MATCH = "Match"