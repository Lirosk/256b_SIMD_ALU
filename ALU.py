from nmigen import *
from nmigen.back.pysim import *

class ALU(Elaboratable):
    def __init__(self) -> None:
        super().__init__()
        self.a: Signal = Signal(256, reset=0)
        self.b: Signal = Signal(256, reset=0)

        self.f: Signal - Signal(4, reset=0)

        self.res: Signal = Signal(256, reset=0)

    def elaborate(self, platform):
        m = Module()

        print("hash bola-bola")

        if platform is None:
            s = Signal()
            m.d.sync += s.eq(~s)

        return m


def alu_test():
    yield Tick()
    yield Settle()


if __name__ == '__main__':
    alu = ALU()

    sim = Simulator(alu)
    with sim.write_vcd(open('out.vcd', 'w')):
        def proc():
            yield from alu_test(alu)
        sim.add_clock(1e-6)
        sim.add_sync_process(proc)
        sim.run
