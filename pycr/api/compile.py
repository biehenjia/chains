from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Union

import numpy as np

from ..core import CR
from ..program import Program
from ..analysis.lower import lower
from ..analysis import prepare_tape, prepare_parallel, dispatch_parallel
from ..codegen import emit, compile_fn, compile_fn_debug
from .parse import parse


@dataclass
class Kernel:
    _call: Callable
    program: Program
    dtype: np.dtype
    width: int
    threads: int

    @property
    def symbol_names(self) -> list[str]:
        return [s.name for s in self.program.symbols]

    def __call__(self, **grids) -> np.ndarray:
        names = self.symbol_names
        if set(grids) != set(names):
            raise TypeError(
                f"Kernel expected grid kwargs {sorted(names)}, got {sorted(grids)}"
            )

        mapping: dict[str, float] = {}
        lengths: list[int] = []
        for name in names:
            spec = grids[name]
            if not (isinstance(spec, tuple) and len(spec) == 3):
                raise TypeError(
                    f"grid for {name!r} must be a (start, step, length) tuple, got {spec!r}"
                )
            start, step, length = spec
            if int(length) < 1:
                raise ValueError(f"grid length for {name!r} must be >= 1, got {length}")
            mapping[f"{name}_0"] = float(start)
            mapping[f"{name}_h"] = float(step)
            lengths.append(int(length))

        padded = list(lengths)
        if self.width > 1:
            inner = padded[-1]
            rem = inner % self.width
            if rem:
                padded[-1] = inner + (self.width - rem)

        if self.threads > 1 and padded[0] % self.threads != 0:
            raise ValueError(
                f"outer length {padded[0]} must be divisible by threads={self.threads}"
            )

        out = np.zeros(padded, dtype=self.dtype)

        if self.threads == 1:
            tape = prepare_tape(self.program.tape, mapping, self.dtype)
            self._call(out, tape)
        else:
            outer_symbol = self.program.symbols[0]
            tape_batch = prepare_parallel(
                outer_symbol, self.program.tape, padded,
                mapping, self.dtype, self.threads,
            )
            dispatch_parallel(self._call, out, tape_batch, padded)

        if padded != lengths:
            slc = tuple(slice(None, L) for L in lengths)
            return out[slc]
        return out


def compile( expr: Union[str, CR], *, dtype=np.float32, width: int = 1, threads: int = 1, name: str = "kernel", debug: bool = False ) -> Kernel:
    if isinstance(expr, str):
        cr, _ = parse(expr)
    else:
        cr = expr

    program = lower(cr, width)
    module = emit(program, dtype, name)
    cfunc = compile_fn_debug(module, name, program.n_dims) if debug else compile_fn(module, name, program.n_dims)

    return Kernel(
        _call=cfunc,
        program=program,
        dtype=np.dtype(dtype),
        width=width,
        threads=threads,
    )
