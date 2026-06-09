from __future__ import annotations
import dataclasses
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
