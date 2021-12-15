from enum import Enum

class ALU_FUNCS(Enum):
    NONE = 0

    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4

    EQ = 5
    MORE = 6
    LESS = 7

    SHL = 8
    SHR = 9


class DATA_TYPES(Enum):
    _32x8b = 0
    _16x16b = 1
    _8x32b = 2
    _4x64b = 3
