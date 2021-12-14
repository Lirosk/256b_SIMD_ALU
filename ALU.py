from nmigen import *
from nmigen.back.pysim import *
from typing import List
from CONSTS import ALU_FUNCS, DATA_TYPES
from Utils import to_formatted_hex, to_hex

class ALU(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.op1: Signal = Signal(256, reset=0)
        self.op2: Signal = Signal(256, reset=0)
        self.data_type: Signal = Signal(DATA_TYPES, reset=0)
        self.func: Signal = Signal(ALU_FUNCS, reset=0)
        self.res: Signal = Signal(256, reset=0)
        self.buf: Signal = Signal(256, reset=0)

    def elaborate(self, platform):
        m = Module()

        if platform is None:
            m.d.sync += Signal().eq(1)

        with m.Switch(self.func):
            with m.Case(ALU_FUNCS.ADD, ALU_FUNCS.SUB):        
                m.d.comb += list(self.adder_logic_gen())
            with m.Case(ALU_FUNCS.EQ):
                m.d.comb += list(self.equal_logic_gen())

        return m

    def equal_logic_gen(self):
        _op1: Signal = Signal(256)
        _op2: Signal = Signal(256)

        n = 32
        b = 256//n

        yield _op1.eq(self.op1)
        yield _op2.eq(self.op2)

        nXb: List[Signal] = []
        for i in range(n):
            nXb.append(Signal())

        D: Signal = Signal()
        Q: Signal = Signal()
        O: Signal = Signal()

        yield [ 
            D.eq(Mux(self.data_type == DATA_TYPES._16x16b, 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES._8x32b,  1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES._4x64b,  1, 0)),
        ]

        DQO_any: Signal = Signal()
        yield DQO_any.eq(D|Q|O)

        for i in range(0, n, b):
            temp0: Signal = Signal()
            temp1: Signal = Signal()
            temp2: Signal = Signal()
            temp3: Signal = Signal()
            temp4: Signal = Signal()
            temp5: Signal = Signal()
            temp6: Signal = Signal()
            temp7: Signal = Signal()

            yield [
                temp0.eq(_op1[(i)  *b:(i+1)*b] == _op2[(i)  *b:(i+1)*b]),
                temp1.eq(_op1[(i+1)*b:(i+2)*b] == _op2[(i+1)*b:(i+2)*b]),
                temp2.eq(_op1[(i+2)*b:(i+3)*b] == _op2[(i+2)*b:(i+3)*b]),
                temp3.eq(_op1[(i+3)*b:(i+4)*b] == _op2[(i+3)*b:(i+4)*b]),
                temp4.eq(_op1[(i+4)*b:(i+5)*b] == _op2[(i+4)*b:(i+5)*b]),
                temp5.eq(_op1[(i+5)*b:(i+6)*b] == _op2[(i+5)*b:(i+6)*b]),
                temp6.eq(_op1[(i+6)*b:(i+7)*b] == _op2[(i+6)*b:(i+7)*b]),
                temp7.eq(_op1[(i+7)*b:(i+8)*b] == _op2[(i+7)*b:(i+8)*b]),

                nXb[i]  .eq(temp0 & Mux(DQO_any, temp1, 1)),
                nXb[i+1].eq(Mux(DQO_any, 0, temp1)),
                nXb[i+2].eq(temp2 & Mux(DQO_any, temp3, 1)),
                nXb[i+3].eq(Mux(DQO_any, 0, temp3)),
                nXb[i+4].eq(temp4 & Mux(DQO_any, temp5, 1)),
                nXb[i+5].eq(Mux(DQO_any, 0, temp5)),
                nXb[i+6].eq(temp6 & Mux(DQO_any, temp7, 1)),
                nXb[i+7].eq(Mux(DQO_any, 0, temp7)),

                nXb[i]  .eq(temp0 & Mux(DQO_any, temp1, 1) & Mux(Q|O, temp2 & Mux(DQO_any, temp3, 1), 1)),
                nXb[i+2].eq(Mux(Q|O, 0, (temp2 & Mux(DQO_any, temp3, 1)))),
                nXb[i+4].eq(temp4 & Mux(DQO_any, temp5, 1) & Mux(Q|O, temp6 & Mux(DQO_any, temp7, 1), 1)), 
                nXb[i+6].eq(Mux(Q|O, 0, (temp4 & Mux(DQO_any, temp5, 1)))),

                nXb[i]  .eq(temp0 & Mux(DQO_any, temp1, 1) & Mux(Q|O, temp2 & Mux(DQO_any, temp3, 1), 1) & Mux(O, temp4 & Mux(DQO_any, temp5, 1) & Mux(Q|O, temp6 & Mux(DQO_any, temp7, 1), 1), 1)),
                nXb[i+4].eq(Mux(O, 0, temp4 & Mux(DQO_any, temp5, 1) & Mux(Q|O, temp6 & Mux(DQO_any, temp7, 1), 1)))
            ]  


        for i in range(n):
            yield self.res[i*b:(i+1)*b].eq(nXb[i])
        i = 0
        yield self.buf.eq(
            _op1[(i)  *b:(i+1)*b] == _op2[(i)  *b:(i+1)*b]
        )


    def adder_logic_gen(self):
        _op1: Signal = Signal(256)
        _op2: Signal = Signal(256)

        sub: Signal = Signal()
        yield sub.eq(Mux(self.func == ALU_FUNCS.SUB, 1, 0))

        yield _op1.eq(self.op1)
        yield _op2.eq(Mux(sub, ~self.op2, self.op2))

        n = 32
        b = 256//n

        nXb: List[Signal] = []
        for i in range(n):
            nXb.append(Signal(b + 1))

        D: Signal = Signal()
        Q: Signal = Signal()
        O: Signal = Signal()

        yield [ 
            D.eq(Mux(self.data_type == DATA_TYPES._16x16b, 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES._8x32b, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES._4x64b, 1, 0))
        ]

        DQO_any: Signal = Signal()
        yield DQO_any.eq(D|Q|O)

        for i in range(0, n, b):
           yield [
                nXb[i]  .eq(_op1[(i)  *b:(i+1)*b] + _op2[(i)  *b:(i+1)*b] + (sub)),
                nXb[i+1].eq(_op1[(i+1)*b:(i+2)*b] + _op2[(i+1)*b:(i+2)*b] + (sub&(~DQO_any))   + (nXb[i]  [-1]&DQO_any) ),
                nXb[i+2].eq(_op1[(i+2)*b:(i+3)*b] + _op2[(i+2)*b:(i+3)*b] + (sub&(~DQO_any|D)) + (nXb[i+1][-1]&(Q|O))   ),
                nXb[i+3].eq(_op1[(i+3)*b:(i+4)*b] + _op2[(i+3)*b:(i+4)*b] + (sub&(~DQO_any))   + (nXb[i+2][-1]&DQO_any) ),
                nXb[i+4].eq(_op1[(i+4)*b:(i+5)*b] + _op2[(i+4)*b:(i+5)*b] + (sub&(~(O)))       + (nXb[i+3][-1]&(O)) ),
                nXb[i+5].eq(_op1[(i+5)*b:(i+6)*b] + _op2[(i+5)*b:(i+6)*b] + (sub&(~DQO_any))   + (nXb[i+4][-1]&DQO_any) ),
                nXb[i+6].eq(_op1[(i+6)*b:(i+7)*b] + _op2[(i+6)*b:(i+7)*b] + (sub&(~DQO_any|D)) + (nXb[i+5][-1]&(Q|O))   ),
                nXb[i+7].eq(_op1[(i+7)*b:(i+8)*b] + _op2[(i+7)*b:(i+8)*b] + (sub&(~DQO_any))   + (nXb[i+6][-1]&DQO_any) ),
            ]          

        yield self.res.eq(Cat(*[s[:b] for s in nXb]))
        yield self.buf.eq(0)


s: int = 0
f: int = 0
def alu_ut(alu: ALU, func: ALU_FUNCS, op1: str, op2: str, data_type: DATA_TYPES, expected: str):
    global s, f

    yield alu.op1.eq(int(op1, 16))
    yield alu.op2.eq(int(op2, 16))
    yield alu.data_type.eq(data_type)
    yield alu.func.eq(func)

    yield Settle()

    res = to_formatted_hex((yield alu.res))
    
    if res == expected:
        s += 1
    else:
        buf = to_formatted_hex((yield alu.buf))
        print(f'WRONG:\n{op1 = }\n{op2 = }\n{func = }\n{res = }\n{data_type = }\n{expected = }\n{buf = }\n\n')
        f += 1


def alu_test(alu: ALU):
    global s, f

    yield from alu_add_test(alu)
    yield from alu_equal_test(alu)
    
    print(f'{s = }\n{f = }')


def alu_equal_test(alu: ALU):
    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01', 
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01',
        DATA_TYPES._32x8b,
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01',
        DATA_TYPES._32x8b,
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_02',
        DATA_TYPES._32x8b,
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF', 
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF',
        DATA_TYPES._32x8b,
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF', 
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF',
        DATA_TYPES._16x16b,
        '00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF', 
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF',
        DATA_TYPES._8x32b,
        '00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF', 
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF',
        DATA_TYPES._4x64b,
        '00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01'
    )

    
def alu_add_test(alu):
    yield from alu_ut(alu, ALU_FUNCS.ADD,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '1',
        DATA_TYPES._32x8b, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.ADD,
        'AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA_AA',
        '12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12_12',
        DATA_TYPES._32x8b, 
        'BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC_BC'
    )
    yield from alu_ut(alu, ALU_FUNCS.ADD,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01',
        DATA_TYPES._32x8b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.ADD,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01',
        DATA_TYPES._16x16b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.ADD,
        '00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF_00_FF',
        '00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01',
        DATA_TYPES._16x16b, 
        '01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00_01_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.ADD,
        '00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF_00_FF_FF_FF',
        '00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01',
        DATA_TYPES._8x32b, 
        '01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00_01_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.ADD,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        '00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01_00_00_00_00_00_00_00_01',
        DATA_TYPES._4x64b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.SUB,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        DATA_TYPES._32x8b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.SUB, 
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        DATA_TYPES._16x16b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.SUB,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        DATA_TYPES._8x32b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.SUB,
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        'FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF',
        DATA_TYPES._4x64b, 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )


if __name__ == '__main__':
    alu = ALU()

    sim = Simulator(alu)
    with sim.write_vcd(open('out.vcd', 'w')):
        sim.add_clock(1e-6)
        sim.add_sync_process(lambda: (yield from alu_test(alu)))
        sim.run()
