'''
LOTS OF LOGIC TO FIX REGARDING ORDERS!!! 

'''


from llvmlite import ir, binding
from ..core import *

binding.initialize_native_target()
binding.initialize_native_asmprinter()

f64 = ir.DoubleType()
i64 = ir.IntType(64)
f64p = ir.PointerType(f64)

def _intr(mod, name, n=1):
    fnty = ir.FunctionType(f64, [f64] * n)
    return mod .declare_intrinsic(f"llvm.{name}", tys =[f64], fnty=fnty)

def emit_access(builder : ir.IRBuilder, node: CR, tape):
    mod = builder.function.module

    slc = tape[node.start: node.start + len(node)]
    first = builder.load(slc[0])
    if len(slc) > 1:
        second = builder.load(slc[1])
        mid = builder.load(slc[len(node)//2])
    
    if isinstance(node, (CRsum, CRprod, CRsin)): return first
    elif isinstance(node, CRcos): return mid
    elif isinstance(node, CRtan): return builder.fdiv(first, mid)
    elif isinstance(node, CRcot): return builder.fdiv(mid, first)
    elif isinstance(node, CREconnector): return emit_access(builder, node[0], tape)
    elif isinstance(node, CREadd): return builder.add(first, second)
    elif isinstance(node, CREmul): return builder.mul(first, second)
    elif isinstance(node, CREpow): return builder.call(_intr(mod, "pow"), [first])
    elif isinstance(node, CRElog): return builder.call(_intr(mod, "log"), [first])
    elif isinstance(node, CREsin): return builder.call(_intr(mod, "sin"), [first])
    elif isinstance(node, CREcos): return builder.call(_intr(mod, "cos"), [first])
    elif isinstance(node, CREtan): return builder.fdiv(builder.call(_intr(mod, "sin"), [first]), builder.call(_intr(mod, "cos"), [second]))
    elif isinstance(node, CREcot): return builder.fdiv(builder.call(_intr(mod, "cos"), [second]), builder.call(_intr(mod, "sin"), [first]))
    

def emit_shift(builder: ir.IRBuilder, node: CR, tape):
    slc = tape[node.start : node.start + len(node)]
    if isinstance(node, CRsum):
        for i in range(len(slc)-1):
            a = builder.load(slc[i])
            b = builder.load(slc[i+1])
            builder.store(builder.fadd(a,b), slc[i])
    
    elif isinstance(node, CRprod):
        for i in range(len(slc)-1):
            a = builder.load(slc[i])
            b = builder.load(slc[i+1])
            builder.store(builder.fmul(a,b), slc[i])

    
    elif isinstance(node, CRtrig):
        fma = _intr(builder.function.module, "fma", 3)
        t = len(slc)//2
        for i in range(t-1):
            ri = builder.load(slc[i])
            ri1 = builder.load(slc[i + 1])
            rti = builder.load(slc[t + i])
            rti1 = builder.load(slc[t + i + 1])
            a = builder.call(fma, [ri, rti1, builder.fmul(rti, ri1)])
            b = builder.call(fma, [rti, rti1, builder.fneg(builder.fmul(ri, ri1))])
            builder.store(a, slc[i])
            builder.store(b, slc[t + i])

    # either the CREconnector wraps the entirety of the node, or pulls a value in and emits that. Either way,
    # it will be the same as CRE, we just fetch the value of where we
    elif isinstance(node, CREconnector):
        # store our only child into the only slot that we have
        builder.store(emit_access(builder, node[0], tape), slc[0])
    
    elif isinstance(node, CRE):
        for i in range(len(node)):
            if node[i].variable == node.variable:
                builder.store(emit_access(builder, node[i], tape), slc[i])

def linear_idx(builder, idxs, strides):
    acc = builder.mul(idxs[0], strides[0])
    for j, s in zip(idxs[1:], strides[1:]):
        acc = builder.add(acc, builder.mul(j, s))
    return acc


def emit_prologue(builder, tape):
    consts = [ir.Constant(f64, float(v)) for v in tape]
    tape = []
    for c in consts:
        a = builder.alloca(f64)
        builder.store(c,a)
        tape.append(a)
    return tape, consts

def emit_reset(builder, node, tape, consts):
    for i in range(node.start, node.start+ len(node)):
        builder.store(consts[i], tape[i])

# for node in the order-list, and orderlist does not have nonshifts.
# do emit_fetch on the node
def emit_fetch(builder, node, tape):
    
    if isinstance(node, CRE):
        for i, child in enumerate(node):
            # if the child is not a CRnum and has a lesser ordered dependency, then we must propogate
            if not isinstance(child, CRnum) and child.min_order < node.variable :
                # fetch the child by its access pattern into
                builder.store(emit_access(builder, child, tape), tape[node.start+i])
    else:
        for i,child in enumerate(node):
            if isinstance(child, CRnum):
                continue
            if child.variable != node.variable:
                builder.store(emit_access(builder, child, tape), tape [node.start+i])
    
    
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
    builder.cbranch(builder.icmp_signed("<",idx, n), b, x)

    builder.position_at_end(b)
    body_fn(builder, idx)
    latch = builder.block
    nxt = builder.add(idx, ir.Constant(i64, 1))
    idx.add_incoming(nxt, latch)
    builder.branch(h)
    builder.position_at_end(x)

def emit_nested(builder, orders, bounds, work, consts, out_ptr, strides, root, depth=0, indices=()):
    last = depth == len(orders) - 1

    def body(builder, idx):
        idxs = indices + (idx,)
        if last:
            lidx = linear_idx(builder, idxs, strides)
            val = emit_access(builder, root, work)
            ptr = builder.gep(out_ptr, [lidx])
            builder.store(val, ptr)
            for cr in orders[depth]:
                emit_shift(builder, cr, work)
        else:
            for cr in orders[depth]:
                emit_shift(builder, cr, work)
            emit_nested(builder, orders, bounds, work, consts, out_ptr, strides, root, depth + 1, idxs)
            for cr in orders[depth + 1]:
                emit_reset(builder, cr, work, consts)
                emit_fetch(builder, cr, work)

    emit_loop(builder, bounds[depth], body)


def emit_function(module, name, term):
    n = len(term.orders)
    fntype = ir.FunctionType(ir.VoidType(), [f64p] + [i64] * n)
    fn = ir.Function(module, fntype, name=name)
    out_ptr = fn.args[0]
    bounds = list(fn.args[1:])
    out_ptr.name = "A"
    for i, b in enumerate(bounds):
        b.name = f"B_{i}"

    entry = fn.append_basic_block("entry")
    builder = ir.IRBuilder(entry)
    # early exit if any bound is non-positive
    with builder.if_then(builder.icmp_signed('<=', bounds[0], ir.Constant(i64, 0))):
        builder.ret_void()
    for b in bounds[1:]:
        with builder.if_then(builder.icmp_signed('<=', b, ir.Constant(i64, 0))):
            builder.ret_void()
    strides = [None] * n
    strides[-1] = ir.Constant(i64, 1)
    for i in range(n - 2, -1, -1):
        strides[i] = builder.mul(strides[i + 1], bounds[i + 1])

    work, consts = emit_prologue(builder, term.tape)
    root = term.orders[-1][-1]
    emit_nested(builder, term.orders, bounds, work, consts, out_ptr, strides, root)
    builder.ret_void()
    return fn

def compile_cr(term, name="generated", opt=3):
    import ctypes
    if hasattr(term, "prepare"):
        term.prepare()

    module = ir.Module(name="crmod")
    module.triple = binding.get_default_triple()
    emit_function(module, name, term)

    llmod = binding.parse_assembly(str(module))
    llmod.verify()

    tm = binding.Target.from_default_triple().create_target_machine()

    pto = binding.PipelineTuningOptions()
    pto.opt_level = opt
    pto.loop_vectorization = True
    pb = binding.PassBuilder(tm, pto)
    pm = pb.getModulePassManager()
    pm.run(llmod, pb)

    engine = binding.create_mcjit_compiler(llmod, tm)
    engine.finalize_object()

    n = len(term.orders)
    cfntype = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_double), *([ctypes.c_int64] * n))
    cfn = cfntype(engine.get_function_address(name))
    cfn._engine = engine
    cfn._module = llmod
    cfn.ir_unopt = str(module)
    cfn.ir_opt = str(llmod)
    cfn.asm = tm.emit_assembly(llmod)
    return cfn