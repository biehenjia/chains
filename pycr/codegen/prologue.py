from llvmlite import ir
from .registers import *
import sympy, functools


def emit_signature(symbols: list[sympy.Symbol], reg_type: ir.Type)-> ir.FunctionType:
    array_ptr = ir.PointerType(reg_type)
    dim_len = ir.IntType(64)
    params = [array_ptr] + [t for s in symbols for t in (reg_type, reg_type, dim_len)]
    return ir.FunctionType(ir.VoidType(), params)

def emit_entry_block(module: ir.Module, sig: ir.FunctionType, name) -> tuple[ir.Function, ir.IRBuilder]:
    func = ir.Function(module, sig, name=name)
    block =func.append_basic_block("entry")
    builder = ir.IRBuilder(block)
    return func, builder








# def lower(expr: sympy.Expr, sym_map: dict[sympy.Symbol, ir.Value], builder: ir.IRBuilder, reg_type: ir.Type)->ir.Value:
#     if isinstance(expr, sympy.Symbol): return sym_map[expr]
#     if isinstance(expr, sympy.Number): ir.Constant(reg_type, float(expr))
#     if isinstance(expr, sympy.Add): 
#         terms = [lower(t,sym_map, builder, reg_type) for t in expr.args]
#         return functools.reduce(builder.fadd, terms)
#     if isinstance(expr, sympy.Mul):
#         factors = [lower(f,sym_map, builder, reg_type) for f in expr.args]
#         return functools.reduce(builder.fmul, factors)
#     if isinstance(expr, sympy.Pow):
#         base = lower(expr.args[0], sym_map, builder, reg_type)
#         exp = lower(expr.args[1], sym_map, builder, reg_type)
#         return 
#     if isinstance(expr, sympy.cot):
#         arg = lower(expr.args[0], sym_map, builder, reg_type)
#         tan_val = call_intrinsic(builder, "llvm.tan", reg_type, [arg])
#         one = ir.Constant(reg_type, 1.0)
#         return builder.fdiv(one, tan_val)
    
#     intrinsic_map = {
#         sympy.sin: "llvm.sin",
#         sympy.cos: "llvm.cos",
#         sympy.exp: "llvm.exp",
#         sympy.log: "llvm.log",
#         sympy.tan: "llvm.tan",
#     }

#     for sym_fn, llvm_name in intrinsic_map.items():
#         if isinstance(expr, sym_fn):
#             arg = lower(expr.args[0], sym_map, builder, reg_type)
#             return call_intrinsic(builder, llvm_name, reg_type, [arg])

# def emit_seed(func: ir.Function, builder: ir.IRBuilder, symbols: list[sympy.Symbol], tape: list[sympy.Expr], reg_type: ir.Type) -> Registers:
#     sym_map = {sym: func.args[1+i*3] for i , sym in enumerate( symbols)}
#     regs = Registers(builder, [reg_type] * len(tape))
#     for i,expr in enumerate(tape):
#         val = lower(expr, sym_map, builder, reg_type)
#         regs[i] = val
#     return regs