from llvmlite import ir
from .registers import Registers
from .intrinsics import i64
from .._dtype import numpy_to_ir
import sympy, functools, numpy


def _element_type(arr: numpy.ndarray) -> ir.Type:
    width = arr.shape[1] if arr.ndim == 2 else 1
    return numpy_to_ir(arr.dtype, width)

def emit_signature(result, tape):
    base = numpy_to_ir(result.dtype)
    params = [
        ir.PointerType(base),
        ir.PointerType(_element_type(tape)),
        *([i64] * result.ndim)
    ]
    return ir.FunctionType(ir.VoidType(), params)

def emit_entry_block(module: ir.Module, sig: ir.FunctionType, name: str) -> tuple[ir.Function, ir.IRBuilder]:
    func = ir.Function(module, sig, name=name)
    block = func.append_basic_block("entry")
    return func, ir.IRBuilder(block)

# usage: func, builder = emit_entry_block(module, sig, name)
# func.args[1].add_attribute('readonly')
# regs = Registers(builder, [dtype]* n, width)
# regs.prologue(func.args[1], n)