from nmigen import *
from nmigen.back.pysim import *
from typing import List
from CONSTS import DATA_TYPES

class ALU_ADDER(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.op1: Signal = Signal(256, reset=0)
        self.op2: Signal = Signal(256, reset=0)
        self.data_type: Signal = Signal(DATA_TYPES, reset=0)
        self.sub: Signal = Signal()
        self.res: Signal = Signal(256, reset=0)

    def elaborate(self, platform):
        m = Module()

        if platform is None:
            m.d.sync += Signal().eq(1)

        _op1: Signal = Signal(256)
        _op2: Signal = Signal(256)

        m.d.comb += _op1.eq(self.op1)
        m.d.comb += _op2.eq(Mux(self.sub, ~self.op2 + 1, self.op2))

        n = 32
        b = 256//n

        nXb: List[Signal] = []
        
        for i in range(n):
            nXb.append(Signal(b + 1))


        D: Signal = Signal()
        Q: Signal = Signal()
        O: Signal = Signal()

        m.d.comb += [ 
            D.eq(Mux(self.data_type == DATA_TYPES._16x16b, 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES._8x32b, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES._4x64b, 1, 0))
        ]

        for i in range(0, n, b):
            m.d.comb += [
                nXb[i].eq(  _op1[0:8]   + _op2[0:8]),
                nXb[i+1].eq(_op1[8:16]  + _op2[8:16]  + nXb[i]  [-1]& D),
                nXb[i+2].eq(_op1[16:24] + _op2[16:24] + nXb[i+1][-1]& Q),
                nXb[i+3].eq(_op1[24:32] + _op2[24:32] + nXb[i+2][-1]&(D|Q)),
                nXb[i+4].eq(_op1[32:40] + _op2[32:40] + nXb[i+3][-1]& O),
                nXb[i+5].eq(_op1[40:48] + _op2[40:48] + nXb[i+4][-1]&(D|O)),
                nXb[i+6].eq(_op1[48:56] + _op2[48:56] + nXb[i+5][-1]&(Q|O)),
                nXb[i+7].eq(_op1[56:64] + _op2[56:64] + nXb[i+6][-1]&(D|O|Q)),
            ]

        # m.d.comb += self.res.eq(Cat(*nXb))
        m.d.comb += self.res.eq(_op1 + _op2)

        return m



def adder_ut(alu: ALU_ADDER, op1: int, op2: int, sub: int, data_type: DATA_TYPES, expected: int):
    yield alu.op1.eq(op1)
    yield alu.op2.eq(op2)
    yield alu.sub.eq(sub)
    yield alu.data_type.eq(data_type)

    yield Settle()

    res = yield(alu.res)

    print(res)


def adder_test(alu: ALU_ADDER):
    yield from adder_ut(alu, 1, 1, 0, DATA_TYPES._32x8b, 2)


if __name__ == '__main__':
    adder = ALU_ADDER()

    sim = Simulator(adder)
    with sim.write_vcd(open('out.vcd', 'w')):
        sim.add_clock(1e-6)
        sim.add_sync_process(lambda: (yield from adder_test(adder)))
        sim.run()
