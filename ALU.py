from nmigen import *
from nmigen.back.pysim import *
from typing import List
from CONSTS import DATA_TYPES

class ALU_ADDER(Elaboratable):
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

        op1: Signal = Signal(256)
        op2: Signal = Signal(256)

        m.d.comb += op1.eq(self.op1)
        m.d.comb += op2.eq(Mux(self.sub, ~self.op2 + 1, self.op2))

        n = 32
        b = 256//n

        nXb: List[Signal] = []
        
        for i in range(n):
            nXb.append(Signal(b + 1))


        D: Signal = Signal()
        Q: Signal = Signal()
        O: Signal = Signal()

        m.comb += [ 
            D.eq(Mux(self.data_type == DATA_TYPES._16x16b, 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES._8x32b, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES._4x64b, 1, 0))
        ]

        O0: Signal = Signal(b + 1)
        O1: Signal = Signal(b + 1)
        O2: Signal = Signal(b + 1)
        O3: Signal = Signal(b + 1)
        O4: Signal = Signal(b + 1)
        O5: Signal = Signal(b + 1)
        O6: Signal = Signal(b + 1)
        O7: Signal = Signal(b + 1)

        for i in range(n-b, b):
            m.d.comb += [
                nXb[i].eq(  op1[0:8] + op2[0:8]),
                nXb[i+1].eq(op1[0:8] + op2[8:8]   + nXb[i]  [-1]& D),
                nXb[i+2].eq(op1[0:8] + op2[16:24] + nXb[i+1][-1]& Q),
                nXb[i+3].eq(op1[0:8] + op2[24:32] + nXb[i+2][-1]&(D|Q)),
                nXb[i+4].eq(op1[0:8] + op2[32:40] + nXb[i+3][-1]& O),
                nXb[i+5].eq(op1[0:8] + op2[40:48] + nXb[i+4][-1]&(D|O)),
                nXb[i+6].eq(op1[0:8] + op2[48:56] + nXb[i+5][-1]&(Q|O)),
                nXb[i+7].eq(op1[0:8] + op2[56:64] + nXb[i+6][-1]&(D|O|Q)),
            ]

        return m


def alu_test():
    # tests here

    yield Tick()
    yield Settle()


if __name__ == '__main__':
    alu = ALU_ADDER()

    sim = Simulator(alu)
    with sim.write_vcd(open('out.vcd', 'w')):
        def proc():
            yield from alu_test(alu)
        sim.add_clock(1e-6)
        sim.add_sync_process(proc)
        sim.run
