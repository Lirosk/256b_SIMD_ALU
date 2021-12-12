from enum import Enum

class ALU_FUNCS(Enum):
    ADD = 0
    SUB = 2
    MUL = 2
    DIV = 3

    EQ = 4
    MORE = 5

    LSHIFT = 6
    RSHIFT = 7


class DATA_TYPES(Enum):
    _32x8b = 0
    _16x16b = 1
    _8x32b = 2
    _4x64b = 3
