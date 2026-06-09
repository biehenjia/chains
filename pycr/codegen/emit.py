import numpy
from llvmlite import ir

from .._dtype import numpy_to_ir
from ..program import Program
from .policy import ScalarPolicy, VectorPolicy
from .registers import Registers
from .prologue import emit_signature, emit_entry_block
from .generators import generate_nested


def emit(program: Program, dtype: numpy.dtype, name: str = "kernel") -> ir.Module:
    dtype = numpy.dtype(dtype)
    ir_scalar = numpy_to_ir(dtype)
    policy = ScalarPolicy(ir_scalar) if program.width == 1 else VectorPolicy(ir_scalar, program.width)

    # placeholders only used to derive the IR signature
    temp_res = numpy.zeros([1] * program.n_dims, dtype=dtype)
    if program.width > 1:
        tape_np = numpy.zeros((program.n_slots, program.width), dtype=dtype)
    else:
        tape_np = numpy.zeros(program.n_slots, dtype=dtype)

    module = ir.Module(name="kernel")
    ftype = emit_signature(temp_res, tape_np)
    func, builder = emit_entry_block(module, ftype, name)

    regs = Registers(builder, policy, program.n_slots)
    regs.bind(func, program.n_dims)
    regs.prologue(program.n_slots)
    generate_nested(regs, program.traces_byorder, program.env, policy)
    builder.ret_void()

    return module
