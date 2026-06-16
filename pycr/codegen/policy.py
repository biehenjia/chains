from llvmlite import ir


class LanePolicy:
    def __init__(self, scalar_type: ir.Type, W):
        self.scalar_type = scalar_type
        self.W = W
        self.slot_type = ir.VectorType(scalar_type, W) if W > 1 else scalar_type
    
    def store(self, builder: ir.IRBuilder, out_ptr: ir.Value, id:ir.Value, val: ir.Value):
        pass

    def emit_tail(self, builder: ir.IRBuilder, out_ptr:  ir.Value, val: ir.Value, idx: ir.Value, B: ir.Value ):
        pass

class ScalarPolicy(LanePolicy):
    def __init__(self, scalar_type): super().__init__(scalar_type,1)
    def store(self, builder, out_ptr, idx, val): builder.store(val, builder.gep(out_ptr, [idx]))

class VectorPolicy(LanePolicy):
    """
    Docstring for VectorPolicy
    """
    def store(self, builder, out_ptr, idx, val):
        addr = builder.gep(out_ptr, [idx])
        vptr = builder.bitcast(addr, ir.PointerType(self.slot_type))
        builder.store(val, vptr, align=4)
    def emit_tail(self, builder, out_ptr, val, idx, B):
        W = ir.Constant(ir.IntType(64), self.W)
        zero = ir.Constant(ir.IntType(64), 0)
        rem =builder.srem(B, W)
        with builder.if_then(builder.icmp_signed(">", rem, zero)):
            for lane in range(self.W):
                li64 = ir.Constant(ir.IntType(64), lane)
                li32 = ir.Constant(ir.IntType(32), lane)
                with builder.if_then(builder.icmp_signed("<", li64, rem)):
                    elem = builder.extract_element(val, li32)
                    builder.store(elem, builder.gep(out_ptr, [builder.add(idx, li64)]))
        