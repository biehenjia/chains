import numpy as np
from llvmlite import ir

_SCALAR: dict[np.dtype, ir.Type] = {
    np.dtype("float32"): ir.FloatType(),
    np.dtype("float64"): ir.DoubleType(),
    np.dtype("int32"): ir.IntType(32),
    np.dtype("int64"): ir.IntType(64),
}


def numpy_to_ir(dt: np.dtype, width: int = 1) -> ir.Type:
    base = _SCALAR[np.dtype(dt)]
    return ir.VectorType(base, width) if width > 1 else base
