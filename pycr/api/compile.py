from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Union

import numpy as np

from ..core import CR
from ..program import Program
from ..analysis.lower import lower
from ..analysis import dispatch_parallel
from ..codegen import emit, compile_fn, compile_fn_debug
from .parse import parse


@dataclass
class Bound:
    """A Kernel bound to a specific grid: holds the seeded tape and result buffer.

    Calling a Bound dispatches the kernel — no tape evaluation, no allocation.
    Use this when benchmarking throughput or running the same grid repeatedly.
    """
    kernel: "Kernel"
    tape: np.ndarray
    out: np.ndarray
    lengths: list[int]
    padded: list[int]

    def __call__(self) -> np.ndarray:
        if self.kernel.threads == 1:
            self.kernel._call(self.out, self.tape)
        else:
            dispatch_parallel(self.kernel._call, self.out, self.tape, self.padded)
        return self.result

    @property
    def result(self) -> np.ndarray:
        if self.padded != self.lengths:
            return self.out[tuple(slice(None, L) for L in self.lengths)]
        return self.out

    def reseed(self, **grids) -> None:
        """Rebuild the tape with new seeds. Grid lengths must match the original."""
        mapping, lengths = self.kernel._validate_grids(grids)
        if lengths != self.lengths:
            raise ValueError(
                f"reseed must keep same lengths {self.lengths}; got {lengths}. "
                "Call kernel.bind(...) for a new shape."
            )
        self.tape = self.kernel._build_tape(mapping, self.padded)


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

    def bind(self, **grids) -> Bound:
        mapping, lengths = self._validate_grids(grids)
        padded = self._compute_padded(lengths)
        tape = self._build_tape(mapping, padded)
        out = np.zeros(padded, dtype=self.dtype)
        return Bound(self, tape, out, lengths, padded)

    def __call__(self, **grids) -> np.ndarray:
        return self.bind(**grids)()

    # --- internals ---

    def _validate_grids(self, grids: dict) -> tuple[dict[str, float], list[int]]:
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
        return mapping, lengths

    def _compute_padded(self, lengths: list[int]) -> list[int]:
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
        return padded

    def _build_tape(self, mapping: dict[str, float], padded: list[int]) -> np.ndarray:
        if self.threads == 1:
            return self.program.evaluate(mapping, self.dtype)
        outer = self.program.symbols[0]
        outer_0, outer_h = f"{outer.name}_0", f"{outer.name}_h"
        x0, xh = mapping[outer_0], mapping[outer_h]
        chunk = padded[0] // self.threads
        m = dict(mapping)
        tapes = []
        for i in range(self.threads):
            m[outer_0] = x0 + i * chunk * xh
            tapes.append(self.program.evaluate(m, self.dtype))
        return np.stack(tapes, axis=0)


def compile(
    expr: Union[str, CR],
    *,
    dtype=np.float32,
    width: int = 1,
    threads: int = 1,
    name: str = "kernel",
    debug: bool = False,
) -> Kernel:
    if isinstance(expr, str):
        cr = parse(expr)
    else:
        cr = expr

    program = lower(cr, width)
    module = emit(program, dtype, name)
    cfunc = compile_fn_debug(module, name, program.n_dims) if debug else compile_fn(module, name, program.n_dims)

    # Force lambdify now so the first user call doesn't pay for it.
    _ = program._tape_ufunc

    return Kernel(
        _call=cfunc,
        program=program,
        dtype=np.dtype(dtype),
        width=width,
        threads=threads,
    )
