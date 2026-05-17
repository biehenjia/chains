from llvmlite import ir, binding
from ..core import *


i64 = ir.IntType(64)
i32 = ir.IntType(32)

def _intr(mod, name, scalar_type, W, n_args = 1):
    vt = ir.VectorType(scalar_type, W)
    fnty = ir.FunctionType(vt, [vt]*n_args)
    return mod.declare_intrinsic(f"llvm.{name}", tys =[vt], fnty = fnty)

def _intr_fma(mod, scalar_type, W):
    vt = ir.VectorType(scalar_type, W)
    fnty = ir.FunctionType(vt, [vt,vt,vt])
    return mod.declare_intrinsic("llvm.fma", tys = [vt], fnty=fnty)

def _splat(builder, scalar_val, scalar_type, W):
    vt = ir.VectorType(scalar_type,W )
    undef = ir.Constant(vt, ir.Undefined)
    v = builder.insert_element(undef, scalar_val, ir.Constant(i32,0))
    mask = ir.Constant(ir.VectorType(i32, W), [ir.Constant(i32, 0)] * W)
    return builder.shuffle_vector(v, ir.Constant(vt, ir.Undefined), mask)

def _splat_const(builder, py_val, scalar_type, W):
    return _splat(builder, ir.Constant(scalar_type,py_val), scalar_type, W)

def emit_prologue_vec(builder, tape, scalar_type, W):
    vt = ir.VectorType(scalar_type, W)
    consts = []
    work = []
    for v in tape:
        c = _splat_const(builder, float(v), scalar_type, W)
        a = builder.alloca(vt)
        builder.store(c, a)
        consts.append(c)
        work.append(a)
    return work, consts

def emit_reset_vec(builder, node, work, consts):
    for i in range(node.start, node.start+len(node)):
        builder.store(consts[i], work[i])

def emit_access_vec(builder, node, work ,scalar_type, W):
    mod = builder.function.module
    slc = work[node.start: node.start+len(node)]

    def ld(slot): return builder.load(slot)
    first = ld(slc[0])
    if len(slc) > 1:
        second = ld(slc[1])
        mid = ld(slc[len(node)//2])
    if isinstance(node, (CRsum, CRprod, CRsin)): return first
    elif isinstance(node, CRcos): return mid
    elif isinstance(node, CRtan): return builder.fdiv(first, mid)
    elif isinstance(node, CRcot): return builder.fdiv(mid, first)
    elif isinstance(node, CREconnector): return emit_access_vec(builder, node[0], work,scalar_type, W)
    elif isinstance(node, CREadd): return builder.fadd(first, second)
    elif isinstance(node, CREmul): return builder.fmul(first, second)
    elif isinstance(node, CREpow): return builder.call(_intr(mod, "pow", scalar_type, W, 2), [first, second])
    elif isinstance(node, CRElog): return builder.call(_intr(mod, "log",  scalar_type, W),    [first])
    elif isinstance(node, CREsin): return builder.call(_intr(mod, "sin",  scalar_type, W),    [first])
    elif isinstance(node, CREcos): return builder.call(_intr(mod, "cos",  scalar_type, W),    [first])
    elif isinstance(node, CREtan):
        s = builder.call(_intr(mod, "sin", scalar_type, W), [first])
        c = builder.call(_intr(mod, "cos", scalar_type, W), [first])
        return builder.fdiv(s, c)
    elif isinstance(node, CREcot):
        s = builder.call(_intr(mod, "sin", scalar_type, W), [first])
        c = builder.call(_intr(mod, "cos", scalar_type, W), [first])
        return builder.fdiv(c, s)
    
def emit_shift_vec(builder, node, work, scalar_type, W):
    mod = builder.function.module
    slc = work[node.start : node.start + len(node)]
 
    def ld(slot): return builder.load(slot)
    def st(v, sl): builder.store(v, sl)
 
    if isinstance(node, CRsum):
        for i in range(len(slc) - 1):
            st(builder.fadd(ld(slc[i]), ld(slc[i+1])), slc[i])
 
    elif isinstance(node, CRprod):
        for i in range(len(slc) - 1):
            st(builder.fmul(ld(slc[i]), ld(slc[i+1])), slc[i])
 
    elif isinstance(node, CRtrig):
        fma = _intr_fma(mod, scalar_type, W)
        t = len(slc) // 2
        for i in range(t - 1):
            ri = ld(slc[i])
            ri1 = ld(slc[i + 1])
            rti = ld(slc[t + i])
            rti1 = ld(slc[t + i + 1])
            a = builder.call(fma, [ri,  rti1, builder.fmul(rti, ri1)])
            b = builder.call(fma, [rti, rti1, builder.fneg(builder.fmul(ri, ri1))])
            st(a, slc[i])
            st(b, slc[t + i])
 
    elif isinstance(node, CREconnector):
        st(emit_access_vec(builder, node[0], work, scalar_type, W), slc[0])
 
    elif isinstance(node, CRE):
        for i in range(len(node)):
            if node[i].order == node.order:
                st(emit_access_vec(builder, node[i], work, scalar_type, W), slc[i])


def emit_fetch_vec(builder, node, work, scalar_type, W):
    if isinstance(node, CRE):
        for i, child in enumerate(node):
            if not isinstance(child, CRnum) and child.min_order < node.order:
                builder.store(
                    emit_access_vec(builder, child, work, scalar_type, W),
                    work[node.start + i]
                )
    else:
        for i, child in enumerate(node):
            if isinstance(child, CRnum):
                continue
            if child.order != node.order:
                builder.store(
                    emit_access_vec(builder, child, work, scalar_type, W),
                    work[node.start + i]
                )

def linear_idx(builder, idxs, strides):
    acc = builder.mul(idxs[0], strides[0])
    for j, s in zip(idxs[1:], strides[1:]):
        acc = builder.add(acc, builder.mul(j, s))
    return acc


def emit_loop(builder, n, body_fn):
    fn = builder.function
    pre = builder.block
    h = fn.append_basic_block("loop.h")
    b = fn.append_basic_block("loop.b")
    x = fn.append_basic_block("loop.x")
 
    builder.branch(h)
    builder.position_at_end(h)
    idx = builder.phi(i64, name="i")
    idx.add_incoming(ir.Constant(i64, 0), pre)
    builder.cbranch(builder.icmp_signed("<", idx, n), b, x)
 
    builder.position_at_end(b)
    body_fn(builder, idx)
    latch = builder.block
    nxt = builder.add(idx, ir.Constant(i64, 1))
    idx.add_incoming(nxt, latch)
    builder.branch(h)
    builder.position_at_end(x)


def emit_nested_vec(builder, orders, bounds, work, consts, out_ptr, strides, root, scalar_type, W, depth=0, indices=()):
    last = depth == len(orders) - 1
 
    def body(builder, idx):
        idxs = indices + (idx,)
        if last:
            # idx here is the vector-lane index (step=1 in IR, but each write is W scalars)
            lidx = linear_idx(builder, idxs, strides)
            val  = emit_access_vec(builder, root, work, scalar_type, W)
            ptr  = builder.gep(out_ptr, [lidx])
            # cast scalar ptr to vector ptr and store W values at once
            vt   = ir.VectorType(scalar_type, W)
            vptr = builder.bitcast(ptr, ir.PointerType(vt))
            builder.store(val, vptr)
            for cr in orders[depth]:
                emit_shift_vec(builder, cr, work, scalar_type, W)
        else:
            for cr in orders[depth]:
                emit_shift_vec(builder, cr, work, scalar_type, W)
            emit_nested_vec(builder, orders, bounds, work, consts, out_ptr, strides, root, scalar_type, W, depth + 1, idxs)
            for cr in orders[depth + 1]:
                emit_reset_vec(builder, cr, work, consts)
                emit_fetch_vec(builder, cr, work, scalar_type, W)
 
    emit_loop(builder, bounds[depth], body)


def emit_function_vec(module, name, term, scalar_type, W):
    n = len(term.orders)
    fntype = ir.FunctionType(ir.VoidType(), [ir.PointerType(scalar_type)] + [i64] * n)
    fn = ir.Function(module, fntype, name=name)
    out_ptr, *bounds = fn.args
    out_ptr.name = "A"
    for i, b in enumerate(bounds):
        b.name = f"B_{i}"
 
    entry = fn.append_basic_block("entry")
    builder = ir.IRBuilder(entry)
 
    for b in bounds:
        with builder.if_then(builder.icmp_signed("<=", b, ir.Constant(i64, 0))):
            builder.ret_void()
    

    strides = [None] * n
    strides[-1] = ir.Constant(i64, W)   # innermost stride is W, not 1
    for i in range(n - 2, -1, -1):
        strides[i] = builder.mul(strides[i + 1], bounds[i + 1])
 
    work, consts = emit_prologue_vec(builder, term.tape, scalar_type, W)
    root = term.orders[-1][-1]
    emit_nested_vec(builder, term.orders, bounds, work, consts, out_ptr, strides, root, scalar_type, W)
    builder.ret_void()
    return fn


def compile_cr_vec(term, scalar_type, W, name="generated_vec", opt=3):
    """
    scalar_type: an llvmlite IR type, e.g. ir.FloatType() or ir.DoubleType()
    W:           vector width (caller's choice, must match register width)
    """
    import ctypes, numpy as np
 
    if hasattr(term, "prepare"):
        term.prepare()
 
    module        = ir.Module(name="crmod_vec")
    module.triple = binding.get_default_triple()
    emit_function_vec(module, name, term, scalar_type, W)
 
    llmod = binding.parse_assembly(str(module))
    llmod.verify()
 
    tm  = binding.Target.from_default_triple().create_target_machine()
    pto = binding.PipelineTuningOptions()
    pto.opt_level        = opt
    pto.loop_vectorization = True
    pb  = binding.PassBuilder(tm, pto)
    pm  = pb.getModulePassManager()
    pm.run(llmod, pb)
 
    engine = binding.create_mcjit_compiler(llmod, tm)
    engine.finalize_object()
 
    # pick ctypes scalar to match scalar_type
    csc = ctypes.c_float if isinstance(scalar_type, ir.FloatType) else ctypes.c_double
    
    n  = len(term.orders)
    cfntype = ctypes.CFUNCTYPE(None, ctypes.POINTER(csc), *([ctypes.c_int64] * n))
    cfn = cfntype(engine.get_function_address(name))
    cfn._engine  = engine
    cfn._module  = llmod
    cfn.ir_unopt = str(module)
    cfn.ir_opt = str(llmod)
    cfn.asm = tm.emit_assembly(llmod)
    cfn.W = W
    return cfn