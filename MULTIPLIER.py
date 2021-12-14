from nmigen import *
from nmigen.back.pysim import *
from typing import List
from CONSTS import DATA_TYPES
from Utils import to_formatted_hex

class MULTIPLIER(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.op1: Signal = Signal(256, reset=0)
        self.op2: Signal = Signal(256, reset=0)
        self.data_type: Signal = Signal(4, reset=0)
        self.res: Signal = Signal(256, reset=0)
        self.buf: Signal = Signal(256, reset=0)

    def elaborate(self, platform):
        m = Module()

        if platform is None:
            m.d.sync += Signal().eq(1)

        _op1: Signal = Signal(256)
        _op2: Signal = Signal(256)

        m.d.comb += _op1.eq(self.op1)
        m.d.comb += _op2.eq(self.op2)

        n = 32
        b = 256//n

        nXb: List[Signal] = []
        for i in range(n):
            nXb.append(Signal(2*b))

        D: Signal = Signal()
        Q: Signal = Signal()
        O: Signal = Signal()

        m.d.comb += [ 
            D.eq(Mux(self.data_type == DATA_TYPES._16x16b, 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES._8x32b, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES._4x64b, 1, 0))
        ]

        DQO_any: Signal = Signal()
        m.d.comb += DQO_any.eq(D|Q|O)


        for i in range(0, n, b):
            m.d.comb += [
                nXb[i].eq(
                    (
                        ((_op1[(i)*b:(i+1)*b] * _op2[(i)*b:(i+1)*b]) *
                        ((b**((i%b)+1)*_op2[(i+1)*b:(i+2)*b]) & DQO_any))
                        # ((b**((i%b)+2)*_op2[(i+2)*b:(i+3)*b]) & (Q|O)) *
                        # ((b**((i%b)+3)*_op2[(i+3)*b:(i+4)*b]) & (Q|O)) *
                        # ((b**((i%b)+4)*_op2[(i+4)*b:(i+5)*b]) & (O)) *
                        # ((b**((i%b)+5)*_op2[(i+5)*b:(i+6)*b]) & (O)) *
                        # ((b**((i%b)+6)*_op2[(i+6)*b:(i+7)*b]) & (O)) *
                        # ((b**((i%b)+7)*_op2[(i+7)*b:(i+8)*b]) & (O)))
                    )                          
                ),
                nXb[i+1].eq(
                    (
                        ((_op1[(i)*b:(i+1)*b] * _op2[(i)*b:(i+1)*b]) *
                        ((b**((i%b)+1)*_op2[(i+1)*b:(i+2)*b]) & DQO_any) *
                        ((b**((i%b)+2)*_op2[(i+2)*b:(i+3)*b]) & (Q|O)) *
                        ((b**((i%b)+3)*_op2[(i+3)*b:(i+4)*b]) & (Q|O)) *
                        ((b**((i%b)+4)*_op2[(i+4)*b:(i+5)*b]) & (O)) *
                        ((b**((i%b)+5)*_op2[(i+5)*b:(i+6)*b]) & (O)) *
                        ((b**((i%b)+6)*_op2[(i+6)*b:(i+7)*b]) & (O)) *
                        ((b**((i%b)+7)*_op2[(i+7)*b:(i+8)*b]) & (O)))
                    )                          
                ),
            ]          

        m.d.comb += self.res.eq(Cat(*[s[:b] for s in nXb]))
        m.d.comb += self.buf.eq(
            _op1
        )
        return m


s: int = 0
f: int = 0
def multiplier_ut(alu: MULTIPLIER, op1: str, op2: str, sub: int, data_type: DATA_TYPES, expected: str):
    global s, f

    yield alu.op1.eq(int(op1, 16))
    yield alu.op2.eq(int(op2, 16))
    yield alu.data_type.eq(data_type)

    yield Settle()

    res = to_formatted_hex((yield alu.res))
    buf = to_formatted_hex((yield alu.buf))    

    if res == expected:
        s += 1
        print(f'{buf = }\n\n')
    else:
        print(f'WRONG:\n{op1 = }\n{op2 = }\n' + ('-' if sub == 1 else '+') + f'\n{res = }\n{data_type = }\n{buf = }\n\n')
        f += 1


def multiplier_test(multiplier: MULTIPLIER):
    global s, f

    yield from multiplier_ut(multiplier,
        '11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11',
        '02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02_02',
        0, DATA_TYPES._32x8b,
        "22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22"
    )

    yield from multiplier_ut(multiplier,
        '11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11',
        '00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02',
        0, DATA_TYPES._16x16b,
        "22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22"
    )

    yield from multiplier_ut(multiplier,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02_00_02',
        0, DATA_TYPES._16x16b,
        "FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE_FF_FE"
    )

    # yield from multiplier_ut(multiplier,
    #     '11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11',
    #     '00_00_00_02_00_00_00_02_00_00_00_02_00_00_00_02_00_00_00_02_00_00_00_02_00_00_00_02_00_00_00_02',
    #     0, DATA_TYPES._8x32b,
    #     "22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22"
    # )

    # yield from multiplier_ut(multiplier,
    #     '11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11_11',
    #     '00_00_00_00_00_00_00_02_00_00_00_00_00_00_00_02_00_00_00_00_00_00_00_02_00_00_00_00_00_00_00_02',
    #     0, DATA_TYPES._4x64b,
    #     "22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22_22"
    # )

    
    print(f'{s = }\n{f = }')


if __name__ == '__main__':
    multiplier = MULTIPLIER()

    sim = Simulator(multiplier)
    with sim.write_vcd(open('out.vcd', 'w')):
        sim.add_clock(1e-6)
        sim.add_sync_process(lambda: (yield from multiplier_test(multiplier)))
        sim.run()

        