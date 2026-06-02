from llvmlite import ir

i64 = ir.IntType(64)
i32 = ir.IntType(32)
i8 = ir.IntType(8)
f64 = ir.DoubleType()
f32 = ir.FloatType()


def _vsuffix(scalar_type, W):
    if isinstance(scalar_type, ir.FloatType): return f"v{W}f32"
    elif isinstance(scalar_type, ir.DoubleType): return f"v{W}f64"
    raise TypeError(scalar_type)

def _scalar_suffix(scalar_type):
    if isinstance(scalar_type, ir.FloatType): return "f32"
    elif isinstance(scalar_type, ir.DoubleType): return "f64"
    raise TypeError(scalar_type)

def _declare(mod, name, fnty):
    if name in mod.globals: return mod.globals[name]
    return ir.Function(mod, fnty, name=name)

def _scalar_intr(mod, name, scalar_type, n_args=1):
    fnty = ir.FunctionType(scalar_type, [scalar_type] * n_args)
    return _declare(mod, f"llvm.{name}.{_scalar_suffix(scalar_type)}", fnty)


class LanePolicy:

    def __init__(self, scalar_type):
        self.scalar_type = scalar_type
    
    @property
    def W(self): raise NotImplementedError

    @property
    def slot_type(self): raise NotImplementedError
    def make_tape_const(self, entry): raise NotImplementedError
    def store_out(self, builder, out_ptr, lidx, val): raise NotImplementedError
    def get_intrinsic(self, mod, name, n_args=1): raise NotImplementedError
    def alloca_slot(self, builder): return builder.alloca(self.slot_type)

    def get_fma(self, mod): return self.get_intrinsic(mod, "fma", 3)

    @property
    def inner_stride(self): return ir.Constant(i64, self.W)

    def inner_trip(self, builder, B): raise NotImplementedError
    def emit_tail(self, builder, root, work, out_ptr, tail_lidx, B_inner_ir, starts):
        pass 


class ScalarPolicy(LanePolicy):
    W = 1

    @property
    def slot_type(self): return self.scalar_type

    def make_tape_const(self, entry):
        v = entry[0] if isinstance(entry, (list, tuple)) else entry
        return ir.Constant(self.scalar_type, float(v))

    def store_out(self, builder, out_ptr, lidx, val):
        builder.store(val, builder.gep(out_ptr, [lidx]))

    def get_intrinsic(self, mod, name, n_args=1):
        T = self.scalar_type
        fnty = ir.FunctionType(T, [T] * n_args)
        return _declare(mod, f"llvm.{name}.{_scalar_suffix(T)}", fnty)

    def inner_trip(self, builder, B):
        return B


class VectorPolicy(LanePolicy):
    def __init__(self, scalar_type, W):
        super().__init__(scalar_type)
        self._W = W

    @property
    def W(self): return self._W

    @property
    def slot_type(self): return ir.VectorType(self.scalar_type, self._W)

    def make_tape_const(self, entry):
        vals = entry if isinstance(entry, (list, tuple)) else [entry] * self._W
        vt = self.slot_type
        return ir.Constant(vt, [ir.Constant(self.scalar_type, float(v)) for v in vals])

    def store_out(self, builder, out_ptr, lidx, val):
        ptr = builder.gep(out_ptr, [lidx])
        vptr = builder.bitcast(ptr, ir.PointerType(self.slot_type))
        builder.store(val, vptr)

    def get_intrinsic(self, mod, name, n_args=1):
        vt = self.slot_type
        fnty = ir.FunctionType(vt, [vt] * n_args)
        return _declare(mod, f"llvm.{name}.{_vsuffix(self.scalar_type, self._W)}", fnty)

    def inner_trip(self, builder, B):
        return builder.sdiv(B, ir.Constant(i64, self._W))

    def splat(self, builder, scalar_val):
        W = self._W
        vt = self.slot_type
        undef = ir.Constant(vt, ir.Undefined)
        v = builder.insert_element(undef, scalar_val, ir.Constant(i32, 0))
        mask = ir.Constant(ir.VectorType(i32, W), [ir.Constant(i32, 0)] * W)
        return builder.shuffle_vector(v, ir.Constant(vt, ir.Undefined), mask)

    def emit_tail(self, builder, root, work, out_ptr, tail_lidx, B_inner_ir, starts):
        from .emit import emit_access  # lazy — breaks the policy ↔ emit circular dep
        W = self._W
        residual = builder.srem(B_inner_ir, ir.Constant(i64, W))
        zero_i64 = ir.Constant(i64, 0)

        with builder.if_then(builder.icmp_signed(">", residual, zero_i64)):
            val = emit_access(builder, root.node, root.start, root.length, work, self, starts)
            for lane in range(W):
                lane_i64 = ir.Constant(i64, lane)
                lane_i32 = ir.Constant(i32, lane)
                with builder.if_then(builder.icmp_signed("<", lane_i64, residual)):
                    elem = builder.extract_element(val, lane_i32)
                    ptr = builder.gep(out_ptr, [builder.add(tail_lidx, lane_i64)])
                    builder.store(elem, ptr)
