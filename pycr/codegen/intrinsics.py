from llvmlite import ir

i1  = ir.IntType(1)
i8  = ir.IntType(8)
i16 = ir.IntType(16)
i32 = ir.IntType(32)
i64 = ir.IntType(64)

f32 = ir.FloatType()
f64 = ir.DoubleType()

v2f32 = ir.VectorType(f32,  2)
v4f32 = ir.VectorType(f32,  4)
v8f32 =ir.VectorType(f32, 8)

v2f64 = ir.VectorType(f64, 2)
v4f64 = ir.VectorType(f64, 4)

def vec(scalar_type: ir.Type, width: int) -> ir.VectorType: return ir.VectorType(scalar_type, width)

def call_intrinsic(builder: ir.IRBuilder, name: str, reg_type: ir.Type, args: list) -> ir.Value:
    fn = builder.module.declare_intrinsic(name, [reg_type])
    return builder.call(fn, args)

def call_libfn(builder: ir.IRBuilder, name: str, reg_type: ir.Type, args: list) -> ir.Value:
    module = builder.module
    fntype = ir.FunctionType(reg_type, [reg_type] * len(args))
    fn = module.globals.get(name) or ir.Function(module, fntype, name=name)
    return builder.call(fn, args)

class Math:
    def __init__(self, builder: ir.IRBuilder, reg_type: ir.Type): 
        self.builder = builder
        self.reg_type = reg_type

    def _i(self, name, *args): return call_intrinsic(self.builder, name, self.reg_type, list(args))
    def fma(self, a, b, c): return self._i('llvm.fma',  a, b, c)
    def exp(self, a): return self._i('llvm.exp', a)
    def exp2(self, a): return self._i('llvm.exp2', a)
    def log(self, a): return self._i('llvm.log', a)
    def log2(self, a): return self._i('llvm.log2',a)
    def log10(self, a): return self._i('llvm.log10', a)
    def logab(self, a, b): return self.builder.fdiv(self.log(b), self.log(a))
    def pow(self, a, b): return self._i('llvm.pow', a, b)
    
    def sin(self, a): return self._i('llvm.sin', a)
    def cos(self, a): return self._i('llvm.cos', a)
    def tan(self, a): return self._i('llvm.tan', a)
    def cot(self, a): return self.builder.fdiv(self.cos(a), self.sin(a))

    def add(self, a, b): return self.builder.fadd(a, b)
    def sub(self, a, b): return self.builder.fsub(a, b)
    def mul(self, a, b): return self.builder.fmul(a, b)
    def div(self, a, b): return self.builder.fdiv(a, b)
    def neg(self, a): return self.builder.fneg(a)