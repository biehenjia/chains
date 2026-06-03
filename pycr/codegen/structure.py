from llvmlite import ir
import sympy

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