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
                m.d.comb += list(self.addsub_logic_gen())
            with m.Case(ALU_FUNCS.EQ):
                m.d.comb += list(self.equal_logic_gen())
            with m.Case(ALU_FUNCS.MORE, ALU_FUNCS.LESS):
                m.d.comb += list(self.moreless_logic_gen())
            with m.Case(ALU_FUNCS.SHR, ALU_FUNCS.SHL):
                m.d.comb += list(self.sh_logic_gen())

        m.d.comb += self.buf.eq(7)
        m.d.comb += self.buf[0].eq(self.buf[0] & 0)

        return m

    def moreless_logic_gen(self):
        _op1: Signal = Signal(256)
        _op2: Signal = Signal(256)

        n = 32
        b = 256//n

        yield _op1.eq(Mux(self.func == ALU_FUNCS.MORE, self.op1, self.op2))
        yield _op2.eq(Mux(self.func == ALU_FUNCS.MORE, self.op2, self.op1))

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
            temp00: Signal = Signal()
            temp01: Signal = Signal()
            temp02: Signal = Signal()
            temp03: Signal = Signal()
            temp04: Signal = Signal()
            temp05: Signal = Signal()
            temp06: Signal = Signal()
            temp07: Signal = Signal()

            temp10: Signal = Signal()
            temp12: Signal = Signal()
            temp14: Signal = Signal()
            temp16: Signal = Signal()

            temp20: Signal = Signal()
            temp24: Signal = Signal()

            yield [
                temp00.eq(_op1[(i)  *b:(i+1)*b] > _op2[(i)  *b:(i+1)*b]),
                temp01.eq(_op1[(i+1)*b:(i+2)*b] > _op2[(i+1)*b:(i+2)*b]),
                temp02.eq(_op1[(i+2)*b:(i+3)*b] > _op2[(i+2)*b:(i+3)*b]),
                temp03.eq(_op1[(i+3)*b:(i+4)*b] > _op2[(i+3)*b:(i+4)*b]),
                temp04.eq(_op1[(i+4)*b:(i+5)*b] > _op2[(i+4)*b:(i+5)*b]),
                temp05.eq(_op1[(i+5)*b:(i+6)*b] > _op2[(i+5)*b:(i+6)*b]),
                temp06.eq(_op1[(i+6)*b:(i+7)*b] > _op2[(i+6)*b:(i+7)*b]),
                temp07.eq(_op1[(i+7)*b:(i+8)*b] > _op2[(i+7)*b:(i+8)*b]),

                temp10.eq(Mux(DQO_any, temp01, temp00)),
                nXb[i+1].eq(Mux(DQO_any, 0, temp01)),
                temp12.eq(Mux(DQO_any, temp03, temp02)),
                nXb[i+3].eq(Mux(DQO_any, 0, temp03)),
                temp14.eq(Mux(DQO_any, temp05, temp04)),
                nXb[i+5].eq(Mux(DQO_any, 0, temp05)),
                temp16.eq(Mux(DQO_any, temp07, temp06)),
                nXb[i+7].eq(Mux(DQO_any, 0, temp07)),

                temp20.eq(Mux(Q|O, temp12, temp10)),
                nXb[i+2].eq(Mux(Q|O, 0, temp12)),
                temp24.eq(Mux(Q|O, temp16, temp14)),
                nXb[i+6].eq(Mux(Q|O, 0, temp16)),

                nXb[i]  .eq(Mux(O, temp24, temp20)),
                nXb[i+4].eq(Mux(O, 0, temp24)),
            ]  


        for i in range(n):
            yield self.res[i*b:(i+1)*b].eq(nXb[i])
        
        
        for i in range(0, 1):
            temp00: Signal = Signal()
            temp01: Signal = Signal()
            temp02: Signal = Signal()
            temp03: Signal = Signal()
            temp04: Signal = Signal()
            temp05: Signal = Signal()
            temp06: Signal = Signal()
            temp07: Signal = Signal()

            temp10: Signal = Signal()
            temp12: Signal = Signal()
            temp14: Signal = Signal()
            temp16: Signal = Signal()

            temp20: Signal = Signal()
            temp24: Signal = Signal()

            eq1: Signal = Signal()
            eq3: Signal = Signal()
            eq5: Signal = Signal()
            eq7: Signal = Signal()

            yield [
                eq1.eq(_op1[(i+1)*b:(i+2)*b] == _op2[(i+1)*b:(i+2)*b]),
                eq3.eq(_op1[(i+3)*b:(i+4)*b] == _op2[(i+3)*b:(i+4)*b]),
                eq5.eq(_op1[(i+5)*b:(i+6)*b] == _op2[(i+5)*b:(i+6)*b]),
                eq7.eq(_op1[(i+7)*b:(i+8)*b] == _op2[(i+7)*b:(i+8)*b]),

                temp00.eq(_op1[(i)  *b:(i+1)*b] > _op2[(i)  *b:(i+1)*b]),
                temp01.eq(_op1[(i+1)*b:(i+2)*b] > _op2[(i+1)*b:(i+2)*b]),
                temp02.eq(_op1[(i+2)*b:(i+3)*b] > _op2[(i+2)*b:(i+3)*b]),
                temp03.eq(_op1[(i+3)*b:(i+4)*b] > _op2[(i+3)*b:(i+4)*b]),
                temp04.eq(_op1[(i+4)*b:(i+5)*b] > _op2[(i+4)*b:(i+5)*b]),
                temp05.eq(_op1[(i+5)*b:(i+6)*b] > _op2[(i+5)*b:(i+6)*b]),
                temp06.eq(_op1[(i+6)*b:(i+7)*b] > _op2[(i+6)*b:(i+7)*b]),
                temp07.eq(_op1[(i+7)*b:(i+8)*b] > _op2[(i+7)*b:(i+8)*b]),

                temp10.eq(Mux(DQO_any & (~eq1), temp01, temp00)),
                nXb[i+1].eq(Mux(DQO_any, 0, temp01)),
                temp12.eq(Mux(DQO_any & (~eq3), temp03, temp02)),
                nXb[i+3].eq(Mux(DQO_any, 0, temp03)),
                temp14.eq(Mux(DQO_any & (~eq5), temp05, temp04)),
                nXb[i+5].eq(Mux(DQO_any, 0, temp05)),
                temp16.eq(Mux(DQO_any & (~eq7), temp07, temp06)),
                nXb[i+7].eq(Mux(DQO_any, 0, temp07)),

                temp20.eq(Mux(Q|O, temp12, temp10)),
                nXb[i+2].eq(Mux(Q|O, 0, temp12)),
                temp24.eq(Mux(Q|O, temp16, temp14)),
                nXb[i+6].eq(Mux(Q|O, 0, temp16)),

                nXb[i]  .eq(Mux(O, temp24, temp20)),
                nXb[i+4].eq(Mux(O, 0, temp24)),
                ]  

            yield self.buf.eq(
                temp03
            )

    def sh_logic_gen(self):
        _op1: Signal = Signal(256)
        _op2: Signal = Signal(256)

        n = 32
        b = 256//n

        # yield _op1.eq(self.op1)
        yield _op2.eq(self.op2)
        yield _op1.eq(Mux(self.func == ALU_FUNCS.SHL, self.op1, self.op1[::-1]) << _op2)
        
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
            temp00: Signal = Signal()
            temp01: Signal = Signal()
            temp02: Signal = Signal()
            temp03: Signal = Signal()
            temp04: Signal = Signal()
            temp05: Signal = Signal()
            temp06: Signal = Signal()
            temp07: Signal = Signal()

            yield [
                # nXb[i]  .eq(_op1[(i)  *b:(i+1)*b] << _op2),
                # nXb[i+1].eq(_op1[(i+1)*b:(i+2)*b] << _op2),
                # nXb[i+2].eq(_op1[(i+2)*b:(i+3)*b] << _op2),
                # nXb[i+3].eq(_op1[(i+3)*b:(i+4)*b] << _op2),
                # nXb[i+4].eq(_op1[(i+4)*b:(i+5)*b] << _op2),
                # nXb[i+5].eq(_op1[(i+5)*b:(i+6)*b] << _op2),
                # nXb[i+6].eq(_op1[(i+6)*b:(i+7)*b] << _op2),
                # nXb[i+7].eq(_op1[(i+7)*b:(i+8)*b] << _op2),

                temp00.eq(_op1[(i)  *b:(i+1)*b]),
                temp01.eq(_op1[(i+1)*b:(i+2)*b]),
                temp02.eq(_op1[(i+2)*b:(i+3)*b]),
                temp03.eq(_op1[(i+3)*b:(i+4)*b]),
                temp04.eq(_op1[(i+4)*b:(i+5)*b]),
                temp05.eq(_op1[(i+5)*b:(i+6)*b]),
                temp06.eq(_op1[(i+6)*b:(i+7)*b]),
                temp07.eq(_op1[(i+7)*b:(i+8)*b]),


                nXb[i+4].eq(Mux(Q|D,        temp04 << _op2, temp04)),

                nXb[i+2].eq(Mux(D,          temp02 << _op2, temp02)),
                nXb[i+6].eq(Mux(D,          temp06 << _op2, temp06)),

                nXb[i+1].eq(Mux(~(DQO_any), temp01 << _op2, temp01)),
                nXb[i+3].eq(Mux(~(DQO_any), temp03 << _op2, temp03)),
                nXb[i+5].eq(Mux(~(DQO_any), temp05 << _op2, temp05)),
                nXb[i+7].eq(Mux(~(DQO_any), temp07 << _op2, temp07)),
            ]
            


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
            temp00: Signal = Signal()
            temp01: Signal = Signal()
            temp02: Signal = Signal()
            temp03: Signal = Signal()
            temp04: Signal = Signal()
            temp05: Signal = Signal()
            temp06: Signal = Signal()
            temp07: Signal = Signal()

            temp10: Signal = Signal()
            temp12: Signal = Signal()
            temp14: Signal = Signal()
            temp16: Signal = Signal()

            temp20: Signal = Signal()
            temp24: Signal = Signal()

            yield [
                temp00.eq(_op1[(i)  *b:(i+1)*b] == _op2[(i)  *b:(i+1)*b]),
                temp01.eq(_op1[(i+1)*b:(i+2)*b] == _op2[(i+1)*b:(i+2)*b]),
                temp02.eq(_op1[(i+2)*b:(i+3)*b] == _op2[(i+2)*b:(i+3)*b]),
                temp03.eq(_op1[(i+3)*b:(i+4)*b] == _op2[(i+3)*b:(i+4)*b]),
                temp04.eq(_op1[(i+4)*b:(i+5)*b] == _op2[(i+4)*b:(i+5)*b]),
                temp05.eq(_op1[(i+5)*b:(i+6)*b] == _op2[(i+5)*b:(i+6)*b]),
                temp06.eq(_op1[(i+6)*b:(i+7)*b] == _op2[(i+6)*b:(i+7)*b]),
                temp07.eq(_op1[(i+7)*b:(i+8)*b] == _op2[(i+7)*b:(i+8)*b]),

                temp10.eq(temp00 & Mux(DQO_any, temp01, 1)),
                nXb[i+1].eq(Mux(DQO_any, 0, temp01)),
                temp12.eq(temp02 & Mux(DQO_any, temp03, 1)),
                nXb[i+3].eq(Mux(DQO_any, 0, temp03)),
                temp14.eq(temp04 & Mux(DQO_any, temp05, 1)),
                nXb[i+5].eq(Mux(DQO_any, 0, temp05)),
                temp16.eq(temp06 & Mux(DQO_any, temp07, 1)),
                nXb[i+7].eq(Mux(DQO_any, 0, temp07)),

                temp20.eq(temp10 & Mux(Q|O, temp12, 1)),
                nXb[i+2].eq(Mux(Q|O, 0, temp12)),
                temp24.eq(temp14 & Mux(Q|O, temp16, 1)), 
                nXb[i+6].eq(Mux(Q|O, 0, temp14)),

                nXb[i]  .eq(temp20 & Mux(O, temp24, 1)),
                nXb[i+4].eq(Mux(O, 0, temp24)),
            ]  


        for i in range(n):
            yield self.res[i*b:(i+1)*b].eq(nXb[i])


    def addsub_logic_gen(self):
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

    yield from alu_moreless_test(alu)
    yield from alu_addsub_test(alu)
    yield from alu_equal_test(alu)
    yield from alu_sh_test(alu)
    
    print(f'{s = }\n{f = }')

def alu_sh_test(alu: ALU):
    yield from alu_ut(alu, ALU_FUNCS.SHL, 
        "00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00",
        "00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00",
        DATA_TYPES._32x8b,
        "00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00"
    )


def alu_moreless_test(alu: ALU):
    yield from alu_ut(alu, ALU_FUNCS.MORE,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00',
        DATA_TYPES._32x8b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.MORE,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_0B_0A_09_08_07_06_05_04_03_02_01_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01_01_01_01_01_01_01_01_01_01_01',
        DATA_TYPES._32x8b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01_01_01_01_01_01_01_01_01_01_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.MORE,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_10_00_00_23_23_00_00_01', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_23_00_00_23_01_00',
        DATA_TYPES._16x16b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01_00_00_00_01_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.MORE,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'01_00_00_00_'+'00_01_01_01_'+'00_10_00_00_'+'00_01_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_01_01_01_'+'01_00_00_00_'+'01_00_00_00_'+'00_00_01_00',
        DATA_TYPES._8x32b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_00_00_01_'+'00_00_00_00_'+'00_00_00_00_'+'00_00_00_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.MORE,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'01_00_00_00_00_01_01_01_'+'00_10_00_00_00_01_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_01_01_01_01_00_00_00_'+'01_00_00_00_00_00_01_00',
        DATA_TYPES._4x64b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_00_00_00_00_00_00_01_'+'00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.LESS,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00',
        DATA_TYPES._32x8b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.LESS,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_0B_0A_09_08_07_06_05_04_03_02_01_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01_01_01_01_01_01_01_01_01_01_01',
        DATA_TYPES._32x8b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.LESS,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_10_00_00_23_23_00_00_01', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_23_00_00_23_01_00',
        DATA_TYPES._16x16b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_01_00_00_00_01'
    )

    yield from alu_ut(alu, ALU_FUNCS.LESS,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'01_00_00_00_'+'00_01_01_01_'+'00_10_00_00_'+'00_01_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_01_01_01_'+'01_00_00_00_'+'01_00_00_00_'+'00_00_01_00',
        DATA_TYPES._8x32b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_00_00_00_'+'00_00_00_01_'+'00_00_00_01_'+'00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.LESS,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'01_00_00_00_00_01_01_01_'+'00_10_00_00_00_01_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_01_01_01_01_00_00_00_'+'01_00_00_00_00_00_01_00',
        DATA_TYPES._4x64b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_'+'00_00_00_00_00_00_00_00_'+'00_00_00_00_00_00_00_01'
    )


def alu_equal_test(alu: ALU):
    yield from alu_ut(alu, ALU_FUNCS.EQ,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00',
        DATA_TYPES._32x8b,
        '01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01_01'
    )

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

    
def alu_addsub_test(alu: ALU):
    yield from alu_ut(alu, ALU_FUNCS.MORE,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00',
        DATA_TYPES._32x8b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

    yield from alu_ut(alu, ALU_FUNCS.SUB,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00', 
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00',
        DATA_TYPES._32x8b,
        '00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00'
    )

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
