from .lower import lower
from .scheduler import construct_tape, vectorize_tape, extract_symbols, partition_orders
from .subexpressions import prepare_cse, cse
from .parallel import dispatch_parallel

import numpy, sympy
from ..core import CR
from ..codegen import compile_fn, emit


__all__ = [
    "prepare_function", "prepare_parallel", "prepare_tape", "dispatch_parallel",
    "lower",
    "construct_tape", "vectorize_tape", "extract_symbols", "partition_orders",
    "prepare_cse", "cse",
]


def prepare_function(cr: CR, dtype=numpy.float32, width: int = 1, name: str = "function"):
    program = lower(cr, width)
    module = emit(program, dtype, name)
    f = compile_fn(module, name, program.n_dims)
    return f, program.tape


def prepare_tape(
    tape: list[sympy.Expr] | list[list[sympy.Expr]],
    mapping: dict[str, tuple[float, float]],
    dtype=numpy.float32,
):
    if isinstance(tape[0], list):
        pretape = [[v.subs(mapping) for v in entry] for entry in tape]
    else:
        pretape = [v.subs(mapping) for v in tape]
    return numpy.array(pretape, dtype=dtype)


def prepare_parallel(lowest_variable, tape, bounds, mapping, dtype, N):
    symbol_0, symbol_h = f"{lowest_variable.name}_0", f"{lowest_variable.name}_h"
    outer_bound = bounds[0]
    assert outer_bound % N == 0, (
        f"prepare_parallel requires outer bound ({outer_bound}) divisible by N ({N}); "
        "per-chunk x_0 shift uses floor division and will misalign otherwise."
    )

    mapping = mapping.copy()
    x0 = mapping[symbol_0]
    xh = mapping[symbol_h]

    tapes = []
    for i in range(N):
        mapping[symbol_0] = x0 + i * (outer_bound // N) * xh
        tapes.append(prepare_tape(tape, mapping, dtype))
    return numpy.array(tapes, dtype=dtype)
