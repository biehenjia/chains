from llvmlite import ir
from .intrinsics import *

class Registers(Math):
    # dtypes are homogenous
    def __init__(self, builder: ir.IRBuilder, dtypes: list[ir.Type], width):
        self.builder = builder
        self.slots: list[ir.AllocaInstr] = [builder.alloca(t, name=f"r{i}") for i,t in enumerate(dtypes)]
        self.constants: list[ir.AllocaInstr] = []
        self.rtype = dtypes[0]
        Math.__init__(self, builder, self.rtype)

    def __getitem__(self, i ): return self.builder.load(self.slots[i])
    def __setitem__(self, i, value): self.builder.store(value, self.slots[i])
    def __len__(self): return len(self.slots)


