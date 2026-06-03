from llvmlite import ir
import sympy

i32 = ir.IntType(32)
i64 = ir.IntType(64)
f32 = ir.FloatType(32)
f64 = ir.FloatType(64)
v4f32 = ir.VectorType(f32, 4)
v2f32 = ir.VectorType(f32, 2)
v2f64 = ir.VectorType(f64, 2)

class Registers:
    def __init__(self, builder: ir.IRBuilder, types: list[ir.Type]):
        self.builder = builder
        self.slots: list[ir.AllocaInstr] = [builder.alloca(t, name=f"r{i}") for i,t in enumerate(types)]
    def __getitem__(self, i ): return self.builder.load(self.slots[i])
    def __setitem__(self, i, value): self.builder.store(value, self.slots[i])
    def __len__(self): return len(self.slots)


def call_intrinsic(builder: ir.IRBuilder, name, reg_type: ir.Type, args: list[ir.Value])-> ir.Value:
    module = builder.module
    fntype = ir.FunctionType(reg_type, [reg_type] * len(args))

    if name not in module.globals:
        fn = ir.Function(module, fntype, name = name)
    else:
        fn = module.globals[name]
    return builder.call(fn, args)