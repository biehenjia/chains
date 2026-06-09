import numpy

from .api import parse, crmake, compile, Kernel
from .core import (
    CR, CRnum, CRsum, CRprod,
    CRtrig, CRsin, CRcos, CRtan, CRcot,
    CRE, CREadd, CREmul, CREpow, CRElog,
    CREsin, CREcos, CREtan, CREcot, CREconnector,
    sin, cos, tan, cot, log,
)
from .analysis import prepare_function, prepare_parallel, prepare_tape, dispatch_parallel


def produce_pair(s, dtype=numpy.float32, width=4):
    cr, _ = parse(s)
    return prepare_function(cr, dtype=numpy.dtype(dtype), width=width)


__all__ = [
    # api
    "parse", "crmake", "compile", "Kernel", "produce_pair",
    # CR types
    "CR", "CRnum", "CRsum", "CRprod",
    "CRtrig", "CRsin", "CRcos", "CRtan", "CRcot",
    "CRE", "CREadd", "CREmul", "CREpow", "CRElog",
    "CREsin", "CREcos", "CREtan", "CREcot", "CREconnector",
    "sin", "cos", "tan", "cot", "log",
    # pipeline (transitional — moves to pycr.pipeline once extracted)
    "prepare_function", "prepare_parallel", "prepare_tape", "dispatch_parallel",
]
