from nmigen import *
from nmigen.back.pysim import *
from typing import List
from CONSTS import DATA_TYPES

class ALU_MULTIPLIER(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.op1: Signal = Signal(256, reset=0)
        self.op2: Signal = Signal(256, reset=0)
        self.data_type: Signal = Signal(4, reset=0)
        self.sub: Signal = Signal()
        self.res: Signal = Signal(256, reset=0)

    def elaborate(self, platform):
        m = Module()

        if platform is None:
            s = Signal()
            m.d.sync += s.eq(~s)

        return m

        