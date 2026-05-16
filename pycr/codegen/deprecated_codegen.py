# from llvmlite import ir, binding
# from ..core import *

# binding.initialize_native_target()
# binding.initialize_native_asmprinter()


# f64 = ir.DoubleType()
# i64 = ir.IntType(64)
# f64p = ir.PointerType(f64)

# def _intr(mod, name, n=1):
#     fnty = ir.FunctionType(f64, [f64] * n)
#     return mod.declare_intrinsic(f"llvm.{name}", tys=[f64], fnty=fnty)

# def emit_crsum(builder, slc):
#     for i in range(len(slc) - 1):
#         a = builder.load(slc[i])
#         b = builder.load(slc[i + 1])
#         builder.store(builder.fadd(a, b), slc[i])

# def emit_crprod(builder, slc):
#     for i in range(len(slc) - 1):
#         a = builder.load(slc[i])
#         b = builder.load(slc[i + 1])
#         builder.store(builder.fmul(a, b), slc[i])

# def emit_crtrig(builder, slc):
#     fma = _intr(builder.function.module, "fma", 3)
#     t = len(slc) // 2
#     for i in range(t - 1):
#         ri = builder.load(slc[i])
#         ri1 = builder.load(slc[i + 1])
#         rti = builder.load(slc[t + i])
#         rti1 = builder.load(slc[t + i + 1])
#         a = builder.call(fma, [ri, rti1, builder.fmul(rti, ri1)])
#         b = builder.call(fma, [rti, rti1, builder.fneg(builder.fmul(ri, ri1))])
#         builder.store(a, slc[i])
#         builder.store(b, slc[t + i])


# # slc length will be the same as the CR's value.

# # for a cresum, there must be 2 values.
# def emit_cre(builder, node)

    


# # CRE access pattern:
# # during the postorder shift, CRE's job will solely be to fetch
# # when they are inevitably accessed, i.e., result = CRE.valueof()
# # or say we have a CRE tower
# #      B.CRE (2)
# #     /     \
# #  A.CRE(2)  C.CRE(2)
# #  ....        ....

# # A's job will be to fetch the relevant information so when we ask for
# # it's valueof, it will be ready. 
# # in this case, we will have: A stores valid information, then C does,
# # then, when B needs to be stored, B will read A's value, which will invoke an access pattern
# # for example if A is a sum, then reading A's value will trigger the sum of A's children
# # Res[...] = B.valueof() <-> Res[...] = prod(B), and B already was prepared beforehand. 


# # TODO:
# '''
# If a child node is the same order as it, then we fetch.
# Otherwise, leave it
# '''
# def emit_cre(builder, node, work):
#     mod = builder.function.module
#     t = type(node)
#     l = _op_val(builder, node[0], work)
#     u = _op_val(builder, node[1], work) if len(node) >= 2 else None

#     if t is CREadd: 
#         v = builder.fadd(l, u)
#     # TODO: update access pattern here 
#     elif t is CREconnector:
#         pass
#     elif t is CREmul: 
#         v = builder.fmul(l, u)
#     elif t is CREsin: 
#         v = builder.call(_intr(mod, "sin"), [l])
#     elif t is CREcos: 
#         v = builder.call(_intr(mod, "cos"), [l])
#     elif t is CREtan:
#         v = builder.fdiv(builder.call(_intr(mod, "sin"), [l]), builder.call(_intr(mod, "cos"), [l]))
#     elif t is CREcot:
#         v = builder.fdiv(builder.call(_intr(mod, "cos"), [l]), builder.call(_intr(mod, "sin"), [l]))
#     elif t is CREpow: 
#         v = builder.call(_intr(mod, "pow", 2), [l, u])
#     elif t is CRElog:
#         v = builder.fdiv(builder.call(_intr(mod, "log"), [l]), builder.call(_intr(mod, "log"), [u]))
#     else:
#         raise NotImplementedError(t)

#     builder.store(v, work[node.start])


# def emit_shift(builder, node, work):
#     slc = work[node.start: node.start + len(node)]
#     if isinstance(node, CRsum): emit_crsum(builder, slc)
#     elif isinstance(node, CRprod): emit_crprod(builder, slc)
#     elif isinstance(node, CRtrig): emit_crtrig(builder, slc)
#     elif isinstance(node, CRE): emit_cre(builder, slc)
#     else: raise NotImplementedError(type(node))


# def emit_prologue(builder, tape):
#     consts = [ir.Constant(f64, float(v)) for v in tape]
#     work = []
#     # store the values of each member of the tape into a register on the tape
#     for c in consts:
#         a = builder.alloca(f64)
#         builder.store(c, a)
#         work.append(a)
#     # a is a register, we store the value of c into a
#     return work, consts


# # reset the CR
# def emit_reset(builder, node, work, consts):
#     for i in range(node.start, node.start + len(node)):
#         builder.store(consts[i], work[i])

# # TODO: fix to directly write via access function
# def emit_fetch(builder, node, work):
#     if isinstance(node, CRE):
#         return
#     for i, op in enumerate(node):
#         if isinstance(op, (CRnum, CRE)):
#             continue
#         builder.store(builder.load(work[op.start]), work[node.start + i])
#     emit_spillover(builder, node, work)


# # TODO: don't need update array, we can directly write to the target
# def emit_spillover(builder, node, work):
#     spill = node.start + len(node)
#     if spill >= len(work):
#         return
#     start = node.start
#     mid = start + len(node) // 2
#     if isinstance(node, (CRsum, CRprod, CRsin)):
#         v = builder.load(work[start])
#     elif isinstance(node, CRcos):
#         v = builder.load(work[mid])
#     elif isinstance(node, CRtan):
#         v = builder.fdiv(builder.load(work[start]), builder.load(work[mid]))
#     elif isinstance(node, CRcot):
#         v = builder.fdiv(builder.load(work[mid]), builder.load(work[start]))
#     else:
#         return
#     builder.store(v, work[spill])

# def emit_load_result(builder, node, work):
#     start = node.start
#     mid = start + len(node) // 2
#     if isinstance(node, (CRsum, CRprod, CRsin, CRE)):
#         return builder.load(work[start])
#     if isinstance(node, CRcos):
#         return builder.load(work[mid])
#     if isinstance(node, CRtan):
#         return builder.fdiv(builder.load(work[start]), builder.load(work[mid]))
#     if isinstance(node, CRcot):
#         return builder.fdiv(builder.load(work[mid]), builder.load(work[start]))
#     if isinstance(node, CRtrig):
#         return builder.load(work[start])
#     raise NotImplementedError(type(node))


# def emit_loop(builder, n, body_fn):
#     fn = builder.function
#     pre = builder.block
#     h = fn.append_basic_block("loop.h")
#     b = fn.append_basic_block("loop.b")
#     x = fn.append_basic_block("loop.x")

#     builder.branch(h)
#     builder.position_at_end(h)
#     idx = builder.phi(i64, name="i")
#     idx.add_incoming(ir.Constant(i64, 0), pre)
#     builder.cbranch(builder.icmp_signed("<", idx, n), b, x)

#     builder.position_at_end(b)
#     body_fn(builder, idx)
#     latch = builder.block
#     nxt = builder.add(idx, ir.Constant(i64, 1))
#     idx.add_incoming(nxt, latch)
#     builder.branch(h)
#     builder.position_at_end(x)


# def linear_idx(builder, idxs, strides):
#     acc = builder.mul(idxs[0], strides[0])
#     for j, s in zip(idxs[1:], strides[1:]):
#         acc = builder.add(acc, builder.mul(j, s))
#     return acc


# def emit_nested(builder, orders, bounds, work, consts, out_ptr, strides, root, depth=0, indices=()):
#     last = depth == len(orders) - 1

#     def body(builder, idx):
#         idxs = indices + (idx,)
#         if last:
#             lidx = linear_idx(builder, idxs, strides)
#             val = emit_load_result(builder, root, work)
#             ptr = builder.gep(out_ptr, [lidx])
#             builder.store(val, ptr)
#             for cr in orders[depth]:
#                 emit_shift(builder, cr, work)
#         else:
#             for cr in orders[depth]:
#                 emit_shift(builder, cr, work)
#             emit_nested(builder, orders, bounds, work, consts, out_ptr, strides, root, depth + 1, idxs)
#             for cr in orders[depth + 1]:
#                 emit_reset(builder, cr, work, consts)
#                 emit_fetch(builder, cr, work)

#     emit_loop(builder, bounds[depth], body)



# def emit_function(module, name, term):
#     n = len(term.orders)
#     fntype = ir.FunctionType(ir.VoidType(), [f64p] + [i64] * n)
#     fn = ir.Function(module, fntype, name=name)
#     out_ptr = fn.args[0]
#     bounds = list(fn.args[1:])
#     out_ptr.name = "A"
#     for i, b in enumerate(bounds):
#         b.name = f"B_{i}"

#     entry = fn.append_basic_block("entry")
#     builder = ir.IRBuilder(entry)

#     strides = [None] * n
#     strides[-1] = ir.Constant(i64, 1)
#     for i in range(n - 2, -1, -1):
#         strides[i] = builder.mul(strides[i + 1], bounds[i + 1])

#     work, consts = emit_prologue(builder, term.tape)
#     root = term.orders[-1][-1]
#     emit_nested(builder, term.orders, bounds, work, consts, out_ptr, strides, root)
#     builder.ret_void()
#     return fn



# def compile_cr(term, name="generated", opt=3):
#     import ctypes
#     if hasattr(term, "prepare"):
#         term.prepare()

#     module = ir.Module(name="crmod")
#     module.triple = binding.get_default_triple()
#     emit_function(module, name, term)

#     llmod = binding.parse_assembly(str(module))
#     llmod.verify()

#     tm = binding.Target.from_default_triple().create_target_machine()

#     pto = binding.PipelineTuningOptions()
#     pto.opt_level = opt
#     pto.loop_vectorization = True
#     pb = binding.PassBuilder(tm, pto)
#     pm = pb.getModulePassManager()
#     pm.run(llmod, pb)

#     engine = binding.create_mcjit_compiler(llmod, tm)
#     engine.finalize_object()

#     n = len(term.orders)
#     cfntype = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_double), *([ctypes.c_int64] * n))
#     cfn = cfntype(engine.get_function_address(name))
#     cfn._engine = engine
#     cfn._module = llmod
#     cfn.ir_unopt = str(module)
#     cfn.ir_opt = str(llmod)
#     cfn.asm = tm.emit_assembly(llmod)
#     return cfn