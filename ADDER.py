from nmigen import *
from nmigen.back.pysim import *
from typing import List
from CONSTS import DATA_TYPES
from Utils import to_formatted_hex

class ADDER(Elaboratable):
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
        m.d.comb += _op2.eq(Mux(self.sub, ~self.op2, self.op2))

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

        D_or_Q_or_O: Signal = Signal()
        m.d.comb += D_or_Q_or_O.eq(D|Q|O)

        for i in range(0, n, b):
            m.d.comb += [
                nXb[i].eq(  _op1[(i)  *b:(i+1)*b] + _op2[(i)  *b:(i+1)*b] + (self.sub)),
                nXb[i+1].eq(_op1[(i+1)*b:(i+2)*b] + _op2[(i+1)*b:(i+2)*b] + (self.sub&(~D_or_Q_or_O))   + (nXb[i]  [-1]&D_or_Q_or_O) ),
                nXb[i+2].eq(_op1[(i+2)*b:(i+3)*b] + _op2[(i+2)*b:(i+3)*b] + (self.sub&(~D_or_Q_or_O|D)) + (nXb[i+1][-1]&(Q|O))       ),
                nXb[i+3].eq(_op1[(i+3)*b:(i+4)*b] + _op2[(i+3)*b:(i+4)*b] + (self.sub&(~D_or_Q_or_O))   + (nXb[i+2][-1]&D_or_Q_or_O) ),
                nXb[i+4].eq(_op1[(i+4)*b:(i+5)*b] + _op2[(i+4)*b:(i+5)*b] + (self.sub&(~(O)))           + (nXb[i+3][-1]&(O))         ),
                nXb[i+5].eq(_op1[(i+5)*b:(i+6)*b] + _op2[(i+5)*b:(i+6)*b] + (self.sub&(~D_or_Q_or_O))   + (nXb[i+4][-1]&D_or_Q_or_O) ),
                nXb[i+6].eq(_op1[(i+6)*b:(i+7)*b] + _op2[(i+6)*b:(i+7)*b] + (self.sub&(~D_or_Q_or_O|D))  + (nXb[i+5][-1]&(Q|O))       ),
                nXb[i+7].eq(_op1[(i+7)*b:(i+8)*b] + _op2[(i+7)*b:(i+8)*b] + (self.sub&(~D_or_Q_or_O))   + (nXb[i+6][-1]&D_or_Q_or_O) ),
            ]          

        m.d.comb += self.res.eq(Cat(*[s[:b] for s in nXb]))
        return m


s: int = 0
f: int = 0
def adder_ut(alu: ADDER, op1: str, op2: str, sub: int, data_type: DATA_TYPES, expected: str):
    global s, f

    yield alu.op1.eq(int(op1, 16))
    yield alu.op2.eq(int(op2, 16))
    yield alu.sub.eq(sub)
    yield alu.data_type.eq(data_type)

    yield Settle()

    res = to_formatted_hex((yield alu.res))

    if res == expected:
        s += 1
    else:
        
        print(f'WRONG:\n{op1 = }\n{op2 = }\n' + ('-' if sub == 1 else '+') + f'\n{res = }\n{data_type = }\n\n')
        f += 1


def adder_test(alu: ADDER):
    global s, f

    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '1',
        0, DATA_TYPES._32x8b, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_00'
    )

    yield from adder_ut(alu, 
        'AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA',
        '12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12',
        0, DATA_TYPES._32x8b, 
        'BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC'
    )
    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01',
        0, DATA_TYPES._32x8b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01',
        0, DATA_TYPES._16x16b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from adder_ut(alu, 
        '00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF',
        '00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01',
        0, DATA_TYPES._16x16b, 
        '01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00'
    )

    yield from adder_ut(alu, 
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF',
        '00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01',
        0, DATA_TYPES._8x32b, 
        '01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00'
    )

    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01',
        0, DATA_TYPES._4x64b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        1, DATA_TYPES._32x8b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        1, DATA_TYPES._16x16b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        1, DATA_TYPES._8x32b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from adder_ut(alu, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        1, DATA_TYPES._4x64b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    print(f'{s = }\n{f = }')


if __name__ == '__main__':
    adder = ADDER()

    sim = Simulator(adder)
    with sim.write_vcd(open('out.vcd', 'w')):
        sim.add_clock(1e-6)
        sim.add_sync_process(lambda: (yield from adder_test(adder)))
        sim.run()
