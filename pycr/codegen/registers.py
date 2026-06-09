from llvmlite import ir
from .intrinsics import Math, i64
from .policy import LanePolicy

class Registers(Math):
    def __init__(self, builder, policy, n):
        self.builder: ir.IRBuilder = builder
        self.policy: LanePolicy  = policy
        self.rtype = policy.slot_type
        self.slots = [builder.alloca(self.rtype, name=f"r{i}") for i in range(n+1)]
        self.bounds: list[ir.Value] = []
        self.result: ir.Value | None = None
        self.indices = []
        Math.__init__(self, builder, self.rtype)

    def __getitem__(self, i): return self.builder.load(self.slots[i])
    def __setitem__(self, i, v): self.builder.store(v, self.slots[i])
    def __len__(self): return len(self.slots)

    def bind(self, func, n_dims):
        self.result = func.args[0]
        self.bounds = list(func.args[2:2 + n_dims])
        self.tape = func.args[1]
        self.resultv = self.builder.bitcast(self.result, ir.PointerType(self.rtype))

    def prologue(self, n: int):
        self.constants = []
        for i in range(n):
            v = self.builder.load(self.builder.gep(self.tape, [ir.Constant(i64, i)]))
            self.constants.append(v)
            self[i] = v
        

    def store_result(self, idx: list[ir.Value], val: ir.Value):
        self.policy.store(self.builder, self.result, self.linearize(idx), val)

    def linearize(self, indices: list[ir.Value]) -> ir.Value:
        acc = indices[0]
        for idx, bound in zip(indices[1:], self.bounds[1:]):
            acc = self.builder.add(self.builder.mul(acc, bound), idx)
        return acc

def emit_reset(regs: Registers, start, length):
    for i in range(start, start + length):
        regs[i] = regs.constants[i]