from llvmlite import ir
from ..core import *
from .policy import (VectorPolicy, i64, i32, i8, _scalar_intr, _declare)


def emit_prologue(builder, plan, policy, seed_ptr=None):
    tape = plan.tape
    consts = []
    work = []

    for entry in tape:
        c = policy.make_tape_const(entry)
        a = policy.alloca_slot(builder)
        builder.store(c, a)
        consts.append(c)
        work.append(a)

    if seed_ptr is not None:
        for e in plan.orders[0]:
            for i in range(e.length):
                scalar_val = builder.load(builder.gep(seed_ptr, [ir.Constant(i64, e.start + i)]))
                if isinstance(policy, VectorPolicy): val = policy.splat(builder, scalar_val)
                else: val = scalar_val
                builder.store(val, work[e.start + i])
        if len(plan.orders) > 1:
            for e in plan.orders[1]: emit_fetch(builder, e.node, e.start, e.length, work, policy, plan.starts)
    return work, consts

def emit_reset(builder, start, length, work, consts):
    for i in range(start, start + length): builder.store(consts[i], work[i])


def emit_access(builder, node, start, length, work, policy, starts):
    mod = builder.function.module
    slc = work[start: start + length]

    def ld(s): return builder.load(s)

    first = ld(slc[0])
    if len(slc) > 1:
        second = ld(slc[1])
        mid = ld(slc[length // 2])

    if isinstance(node, (CRsum, CRprod, CRsin)): return first
    elif isinstance(node, CRcos): return mid
    elif isinstance(node, CRtan): return builder.fdiv(first, mid)
    elif isinstance(node, CRcot): return builder.fdiv(mid, first)

    elif isinstance(node, CREconnector):
        child = node[0]
        cs, cn = starts[id(child)], len(child)
        child_slc = work[cs: cs + cn]
        cf = ld(child_slc[0])
        cm = ld(child_slc[cn // 2]) if len(child_slc) > 1 else None

        if node.index == -1:
            if isinstance(child, CRtrig) and type(child) != node.parent_type:
                if isinstance(child, CRsin): return cf
                if isinstance(child, CRcos): return cm
                if isinstance(child, CRtan): return builder.fdiv(cf, cm)
                if isinstance(child, CRcot): return builder.fdiv(cm, cf)
            return emit_access(builder, child, cs, cn, work, policy, starts)
        else:
            return ld(child_slc[node.index])

    elif isinstance(node, CREadd): return builder.fadd(first, second)
    elif isinstance(node, CREmul): return builder.fmul(first, second)
    elif isinstance(node, CREpow): return builder.call(policy.get_intrinsic(mod, "pow", 2), [first, second])
    elif isinstance(node, CRElog): return builder.call(policy.get_intrinsic(mod, "log"), [first])
    elif isinstance(node, CREsin): return builder.call(policy.get_intrinsic(mod, "sin"), [first])
    elif isinstance(node, CREcos): return builder.call(policy.get_intrinsic(mod, "cos"), [first])
    elif isinstance(node, (CREtan, CREcot)):
        s = builder.call(policy.get_intrinsic(mod, "sin"), [first])
        c = builder.call(policy.get_intrinsic(mod, "cos"), [first])
        return builder.fdiv(s, c) if isinstance(node, CREtan) else builder.fdiv(c, s)


def emit_shift(builder, node, start, length, work, policy, starts):
    mod = builder.function.module
    slc = work[start: start + length]

    def ld(s): return builder.load(s)
    def st(v, s): builder.store(v, s)

    if isinstance(node):
        for i in range(len(slc) - 1):
            st(builder.fadd(ld(slc[i]), ld(slc[i + 1])), slc[i])

    elif isinstance(node, CRprod):
        for i in range(len(slc) - 1):
            st(builder.fmul(ld(slc[i]), ld(slc[i + 1])), slc[i])

    elif isinstance(node, CRtrig):
        fma = policy.get_fma(mod)
        t = len(slc) // 2
        for i in range(t - 1):
            ri = ld(slc[i])
            ri1 = ld(slc[i + 1])
            rti = ld(slc[t + i])
            rti1 = ld(slc[t + i + 1])
            a = builder.call(fma, [ri,  rti1, builder.fmul(rti,  ri1)])
            b = builder.call(fma, [rti, rti1, builder.fneg(builder.fmul(ri, ri1))])
            st(a, slc[i]); st(b, slc[t + i])

    elif isinstance(node, CREconnector):
        child = node[0]
        cs, cn = starts[id(child)], len(child)
        st(emit_access(builder, child, cs, cn, work, policy, starts), slc[0])

    elif isinstance(node, CRE):
        for i in range(len(node)):
            if node[i].variable == node.variable:
                child = node[i]
                cs, cn = starts[id(child)], len(child)
                st(emit_access(builder, child, cs, cn, work, policy, starts), slc[i])


def emit_fetch(builder, node, start, length, work, policy, starts):
    if isinstance(node, CRE):
        for i, child in enumerate(node):
            if isinstance(child, CRE) and child.least_variable != node.variable:
                cs, cn = starts[id(child)], len(child)
                builder.store(emit_access(builder, child, cs, cn, work, policy, starts), work[start + i])
    else:
        for i, child in enumerate(node):
            if isinstance(child, CRnum) or child.variable == node.variable: continue
            cs, cn = starts[id(child)], len(child)
            builder.store(emit_access(builder, child, cs, cn, work, policy, starts), work[start + i])


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


def linear_idx(builder, idxs, strides):
    acc = builder.mul(idxs[0], strides[0])
    for j, s in zip(idxs[1:], strides[1:]): acc = builder.add(acc, builder.mul(j, s))
    return acc


def emit_nested(builder, orders, true_bounds, adj_bounds, work, consts, out_ptr, strides, root, policy, starts, depth=0, indices=()):
    last = depth == len(orders) - 1

    def body(builder, idx):
        idxs = indices + (idx,)
        if last:
            lidx = linear_idx(builder, idxs, strides)
            val = emit_access(builder, root.node, root.start, root.length, work, policy, starts)
            policy.store_out(builder, out_ptr, lidx, val)
            for e in orders[depth]: emit_shift(builder, e.node, e.start, e.length, work, policy, starts)
        else:
            for e in orders[depth]:
                emit_shift(builder, e.node, e.start, e.length, work, policy, starts)
            emit_nested(builder, orders, true_bounds, adj_bounds, work, consts, out_ptr, strides, root, policy, starts, depth + 1, idxs)
            if depth == len(orders) - 2:
                outer_base = linear_idx(builder, list(idxs), strides[:depth + 1])
                inner_main = builder.mul(adj_bounds[-1], ir.Constant(i64, policy.W))
                tail_lidx = builder.add(outer_base, inner_main)
                policy.emit_tail(builder, root, work, out_ptr, tail_lidx, true_bounds[-1], starts)
            for e in orders[depth + 1]:
                emit_reset(builder, e.start, e.length, work, consts)
                emit_fetch(builder, e.node, e.start, e.length, work, policy, starts)
    emit_loop(builder, adj_bounds[depth], body)



def emit_function(module, name, plan, policy, seed_arg=False):
    n = len(plan.orders)
    T = policy.scalar_type
    Tp = ir.PointerType(T)
    seed_args = [Tp] if seed_arg else []
    fntype = ir.FunctionType(ir.VoidType(), [Tp] + seed_args + [i64] * n)
    fn = ir.Function(module, fntype, name=name)

    out_ptr = fn.args[0]
    seed_ptr = fn.args[1] if seed_arg else None
    arg_base = 2 if seed_arg else 1
    bounds = list(fn.args[arg_base: arg_base + n])
    out_ptr.name = "A"
    if seed_ptr is not None: seed_ptr.name = "seed"
    for i, b in enumerate(bounds): b.name = f"B_{i}"
    entry = fn.append_basic_block("entry")
    builder = ir.IRBuilder(entry)

    for b in bounds:
        with builder.if_then(builder.icmp_signed("<=", b, ir.Constant(i64, 0))): builder.ret_void()

    strides = [None] * n
    strides[-1] = policy.inner_stride
    if n > 1:
        strides[-2] = bounds[-1] 
        for i in range(n - 3, -1, -1): strides[i] = builder.mul(strides[i + 1], bounds[i + 1])

    adj_bounds = list(bounds[:-1]) + [policy.inner_trip(builder, bounds[-1])]

    work, consts = emit_prologue(builder, plan, policy, seed_ptr)
    root = plan.root

    emit_nested(builder, plan.orders, bounds, adj_bounds, work, consts, out_ptr, strides, root, policy, plan.starts)

    if n == 1:
        inner_main = builder.mul(adj_bounds[-1], ir.Constant(i64, policy.W))
        policy.emit_tail(builder, root, work, out_ptr, inner_main, bounds[-1], plan.starts)

    builder.ret_void()
    return fn
