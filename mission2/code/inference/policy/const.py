import enum
from enum import Enum


class TransitionType(Enum):
    C_TO_C = enum.auto()
    C_TO_E = enum.auto()
    C_TO_G = enum.auto()
