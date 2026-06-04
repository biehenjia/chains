from llvmlite import ir
from .registers import *
import sympy, functools, numpy


DTYPE_TO_IR: dict[numpy.dtype, ir.Type] = {
    numpy.dtype("float32"): ir.FloatType(),
    numpy.dtype("float64"): ir.DoubleType(),
    numpy.dtype("int32"):   ir.IntType(32),
    numpy.dtype("int64"):   ir.IntType(64),
}

def _element_type(arr: numpy.ndarray) -> ir.Type:
    base = DTYPE_TO_IR[arr.dtype]
    if arr.ndim == 2:
        return ir.VectorType(base, arr.shape[1])
    return base

def emit_signature(result: numpy.ndarray, tape: numpy.ndarray) -> ir.FunctionType:
    dim_len = ir.IntType(64)
    params = [
        ir.PointerType(_element_type(result)),
        ir.PointerType(_element_type(tape)),
        *([dim_len] * result.ndim),
    ]
    return ir.FunctionType(ir.VoidType(), params)

def emit_entry_block(module: ir.Module, sig: ir.FunctionType, name: str) -> tuple[ir.Function, ir.IRBuilder]:
    func = ir.Function(module, sig, name=name)
    block = func.append_basic_block("entry")
    return func, ir.IRBuilder(block)