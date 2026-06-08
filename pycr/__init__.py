from .api import *
from .codegen import ScalarPolicy, VectorPolicy
from .codegen import i8, i16, i32, i64, f32, f64, v2f32, v4f32, v8f32, v2f64, v4f64
from .core import *
from .analysis import prepare_function, prepare_parallel, prepare_tape, dispatch_parallel
import numpy
from llvmlite import ir

DTYPE_TO_IR: dict[numpy.dtype, ir.Type] = {
    numpy.dtype("float32"): ir.FloatType(),
    numpy.dtype("float64"): ir.DoubleType(),
    numpy.dtype("int32"):   ir.IntType(32),
    numpy.dtype("int64"):   ir.IntType(64),
    numpy.float32: f32,
    numpy.float64: f64,
}

IR_TO_DTYPE = { 
    f32: numpy.float32,
    f64: numpy.float64
}

def produce_pair(s, dtype=f32, width = 4):
    cr, st = parse(s)
    dtype = DTYPE_TO_IR[dtype]
    if width == 1:
        policy = ScalarPolicy(dtype)
    else:
        policy = VectorPolicy(dtype, width)
    dtype = IR_TO_DTYPE[dtype]
    return prepare_function(cr, dtype=dtype, policy = policy)





    