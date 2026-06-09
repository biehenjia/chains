# Rule submodules register decorators on CRalgebra at import time.
# Import them first; then re-export the public names from cr.py, which
# also shadows the rule submodule names (sin/cos/tan/cot/log) with the
# top-level sympy/CR-aware functions defined in cr.py.
from . import add, mul, pow, sin, cos, tan, cot, log

from .cr import (
    CR, CRnum, CRsum, CRprod,
    CRtrig, CRsin, CRcos, CRtan, CRcot,
    CRE, CREadd, CREmul, CREpow, CRElog,
    CREsin, CREcos, CREtan, CREcot, CREconnector,
    sin, cos, tan, cot, log,
    CRalgebra,
)

__all__ = [
    "CR", "CRnum", "CRsum", "CRprod",
    "CRtrig", "CRsin", "CRcos", "CRtan", "CRcot",
    "CRE", "CREadd", "CREmul", "CREpow", "CRElog",
    "CREsin", "CREcos", "CREtan", "CREcot", "CREconnector",
    "sin", "cos", "tan", "cot", "log",
    "CRalgebra",
]

