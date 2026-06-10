from __future__ import annotations
import dataclasses
import functools
import numpy as np
import sympy

from .core import CR
from .crconfig import CRconfig


@dataclasses.dataclass
class Program:
    cr: CR
    env: dict[CR, CRconfig]
    symbols: list[sympy.Symbol]
    tape: list
    traces_byorder: list[list[CR]]
    width: int

    @property
    def n_dims(self) -> int:
        return len(self.symbols)

    @property
    def n_slots(self) -> int:
        return len(self.tape)

    @property
    def seed_symbols(self) -> list[sympy.Symbol]:
        out = []
        for s in self.symbols:
            out.append(sympy.Symbol(f"{s.name}_0"))
            out.append(sympy.Symbol(f"{s.name}_h"))
        return out

    @functools.cached_property
    def _tape_ufunc(self):
        # lambdify the symbolic tape into a numpy callable; called once per
        # Program. Subsequent evaluate() calls skip sympy entirely.
        return sympy.lambdify(self.seed_symbols, self.tape, "numpy")

    def evaluate(self, mapping: dict[str, float], dtype=np.float32) -> np.ndarray:
        seeds = [mapping[str(s)] for s in self.seed_symbols]
        return np.asarray(self._tape_ufunc(*seeds), dtype=dtype)
