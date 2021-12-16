from nmigen import *
from nmigen.back.pysim import *
from typing import List
from CONSTS import ALU_FUNCS, DATA_TYPES
from Utils import to_formatted_hex

class ALU(Elaboratable):
    def __init__(self):
        super().__init__()
        self.op1:       Signal = Signal(256,        reset=0)
        self.op2:       Signal = Signal(256,        reset=0)
        self.data_type: Signal = Signal(DATA_TYPES, reset=0)
        self.func:      Signal = Signal(ALU_FUNCS,  reset=0)
        self.res:       Signal = Signal(256,        reset=0)

    def elaborate(self, platform) -> Module:
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

        return m

    def moreless_logic_gen(self) -> Assign:
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
            D.eq(Mux(self.data_type == DATA_TYPES.pckd_w , 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES.pckd_dw, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES.pckd_qw, 1, 0)),
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
            eq1:    Signal = Signal()
            eq3:    Signal = Signal()
            eq5:    Signal = Signal()
            eq7:    Signal = Signal()
            
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

                temp10  .eq(Mux(DQO_any & (~eq1), temp01, temp00)),
                nXb[i+1].eq(Mux(DQO_any         , 0     , temp01)),
                temp12  .eq(Mux(DQO_any & (~eq3), temp03, temp02)),
                nXb[i+3].eq(Mux(DQO_any         , 0     , temp03)),
                temp14  .eq(Mux(DQO_any & (~eq5), temp05, temp04)),
                nXb[i+5].eq(Mux(DQO_any         , 0     , temp05)),
                temp16  .eq(Mux(DQO_any & (~eq7), temp07, temp06)),
                nXb[i+7].eq(Mux(DQO_any         , 0     , temp07)),
                
                temp20  .eq(Mux(Q|O, temp12, temp10)),
                nXb[i+2].eq(Mux(Q|O, 0,      temp12)),
                temp24  .eq(Mux(Q|O, temp16, temp14)),
                nXb[i+6].eq(Mux(Q|O, 0,      temp16)),
                nXb[i]  .eq(Mux(O  , temp24, temp20)),
                nXb[i+4].eq(Mux(O  , 0,      temp24)),
            ] 

        for i in range(n):
            yield self.res[i*b:(i+1)*b].eq(nXb[i])

    def sh_logic_gen(self) -> Assign:
        _op1: Signal = Signal(256)
        _op2: Signal = Signal(256)

        n = 32
        b = 256//n

        yield _op2.eq(
            Mux((self.data_type == DATA_TYPES.pckd_b) & (self.op2 > b),
                b,
                Mux((self.data_type == DATA_TYPES.pckd_w) & (self.op2 > 2*b),
                    2*b,
                    Mux((self.data_type == DATA_TYPES.pckd_dw) & (self.op2 > 4*b),
                        4*b,
                        Mux((self.data_type == DATA_TYPES.pckd_qw) & (self.op2 > 8*b),
                            8*b,
                            self.op2
                        )
                    )
                )
            )
        )
        yield _op1.eq(Mux(self.func == ALU_FUNCS.SHL, self.op1, self.op1[::-1]) << _op2)
        
        nXb: List[Signal] = []
        for i in range(n):
            nXb.append(Signal(8))

        D: Signal = Signal()
        Q: Signal = Signal()
        O: Signal = Signal()

        yield [ 
            D.eq(Mux(self.data_type == DATA_TYPES.pckd_w , 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES.pckd_dw, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES.pckd_qw, 1, 0)),
        ]

        DQO_any: Signal = Signal()
        yield DQO_any.eq(D|Q|O)

        for_zeros: Signal = Signal(64)
        yield for_zeros.eq((-1 >> _op2) << _op2)

        for i in range(0, n, b):
            temp0q: Signal = Signal(4*b)
            temp1q: Signal = Signal(4*b)

            temp0d: Signal = Signal(2*b)
            temp1d: Signal = Signal(2*b)
            temp2d: Signal = Signal(2*b)
            temp3d: Signal = Signal(2*b)

            yield [
                temp0q.eq((_op1[(i)  *b: (i+4)*b]) & for_zeros),
                temp1q.eq((_op1[(i+4)*b: (i+8)*b]) & Mux(Q, for_zeros, -1)),

                temp0d.eq(temp0q[   :2*b] & Mux(D, for_zeros, -1)),
                temp1d.eq(temp0q[2*b:   ] & Mux(D, for_zeros, -1)),
                temp2d.eq(temp1q[   :2*b] & Mux(D, for_zeros, -1)),
                temp3d.eq(temp1q[2*b:   ] & Mux(D, for_zeros, -1)),

                nXb[i]  .eq(temp0d[ :b] & Mux(DQO_any != 1, for_zeros, -1)),
                nXb[i+1].eq(temp0d[b: ] & Mux(DQO_any != 1, for_zeros, -1)),
                nXb[i+2].eq(temp1d[ :b] & Mux(DQO_any != 1, for_zeros, -1)),
                nXb[i+3].eq(temp1d[b: ] & Mux(DQO_any != 1, for_zeros, -1)),
                nXb[i+4].eq(temp2d[ :b] & Mux(DQO_any != 1, for_zeros, -1)),
                nXb[i+5].eq(temp2d[b: ] & Mux(DQO_any != 1, for_zeros, -1)),
                nXb[i+6].eq(temp3d[ :b] & Mux(DQO_any != 1, for_zeros, -1)),
                nXb[i+7].eq(temp3d[b: ] & Mux(DQO_any != 1, for_zeros, -1)),
            ]

        yield self.res.eq(Mux(self.func == ALU_FUNCS.SHL, Cat(*nXb), Cat(*nXb)[::-1]))
            
    def equal_logic_gen(self) -> Assign:
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
            D.eq(Mux(self.data_type == DATA_TYPES.pckd_w , 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES.pckd_dw, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES.pckd_qw, 1, 0)),
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

                temp10  .eq(temp00 & Mux(DQO_any, temp01, 1     )),
                nXb[i+1].eq(         Mux(DQO_any, 0     , temp01)),
                temp12  .eq(temp02 & Mux(DQO_any, temp03, 1     )),
                nXb[i+3].eq(         Mux(DQO_any, 0     , temp03)),
                temp14  .eq(temp04 & Mux(DQO_any, temp05, 1     )),
                nXb[i+5].eq(         Mux(DQO_any, 0     , temp05)),
                temp16  .eq(temp06 & Mux(DQO_any, temp07, 1     )),
                nXb[i+7].eq(         Mux(DQO_any, 0     , temp07)),

                temp20  .eq(temp10 & Mux(Q|O, temp12, 1     )),
                nXb[i+2].eq(         Mux(Q|O, 0     , temp12)),
                temp24  .eq(temp14 & Mux(Q|O, temp16, 1     )), 
                nXb[i+6].eq(         Mux(Q|O, 0     , temp14)),

                nXb[i]  .eq(temp20 & Mux(O, temp24, 1     )),
                nXb[i+4].eq(         Mux(O, 0     , temp24)),
            ]  

        for i in range(n):
            yield self.res[i*b:(i+1)*b].eq(nXb[i])

    def addsub_logic_gen(self) -> Assign:
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
            D.eq(Mux(self.data_type == DATA_TYPES.pckd_w , 1, 0)),
            Q.eq(Mux(self.data_type == DATA_TYPES.pckd_dw, 1, 0)),
            O.eq(Mux(self.data_type == DATA_TYPES.pckd_qw, 1, 0))
        ]

        DQO_any: Signal = Signal()
        yield DQO_any.eq(D|Q|O)

        for i in range(0, n, b):
           yield [
                nXb[i]  .eq(_op1[(i)  *b:(i+1)*b] + _op2[(i)  *b:(i+1)*b] + (sub)                                       ),
                nXb[i+1].eq(_op1[(i+1)*b:(i+2)*b] + _op2[(i+1)*b:(i+2)*b] + (sub&(~DQO_any))   + (nXb[i]  [-1]&DQO_any) ),
                nXb[i+2].eq(_op1[(i+2)*b:(i+3)*b] + _op2[(i+2)*b:(i+3)*b] + (sub&(~DQO_any|D)) + (nXb[i+1][-1]&(Q|O))   ),
                nXb[i+3].eq(_op1[(i+3)*b:(i+4)*b] + _op2[(i+3)*b:(i+4)*b] + (sub&(~DQO_any))   + (nXb[i+2][-1]&DQO_any) ),
                nXb[i+4].eq(_op1[(i+4)*b:(i+5)*b] + _op2[(i+4)*b:(i+5)*b] + (sub&(~(O)))       + (nXb[i+3][-1]&(O))     ),
                nXb[i+5].eq(_op1[(i+5)*b:(i+6)*b] + _op2[(i+5)*b:(i+6)*b] + (sub&(~DQO_any))   + (nXb[i+4][-1]&DQO_any) ),
                nXb[i+6].eq(_op1[(i+6)*b:(i+7)*b] + _op2[(i+6)*b:(i+7)*b] + (sub&(~DQO_any|D)) + (nXb[i+5][-1]&(Q|O))   ),
                nXb[i+7].eq(_op1[(i+7)*b:(i+8)*b] + _op2[(i+7)*b:(i+8)*b] + (sub&(~DQO_any))   + (nXb[i+6][-1]&DQO_any) ),
            ]          

        yield self.res.eq(Cat(*[sig[:b] for sig in nXb]))

