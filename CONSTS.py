from enum import Enum

class ALU_FUNCS(Enum):
    NONE = 0

    ADD  = 1
    SUB  = 2
    MUL  = 3
    DIV  = 4

    EQ   = 5
    MORE = 6
    LESS = 7

    SHL  = 8
    SHR  = 9


class DATA_TYPES(Enum):
    pckd_b  = 0
    pckd_w  = 1
    pckd_dw = 2
    pckd_qw = 3

