from .crconfig import *
from .dispatch import *
from .generators import *
from .scheduler import *
from .subexpressions import *

def test_scalar(cr: CR):
    env = initialize_env(cr)
    policy = ScalarPolicy(f32)

    res = numpy.zeros(100,dtype=numpy.float32)
    tape = construct_tape(env, cr)
    tape = numpy.zeros(10, dtype=numpy.float32)

    module = ir.Module(name="kernel")
    ftype = emit_signature(res,tape)
    func, builder = emit_entry_block(module, ftype, "penguin")

    regs = Registers(builder, policy,3)
    regs.bind(func, 1)
    regs.prologue(3)
    traces_byorder = partition_orders(env, cr) 
    generate_nested(regs, traces_byorder, env, policy)
    builder.ret_void()
    call = compile_fn(module, "penguin", res.ndim)
    return call

def test_vector(cr: CR):
    env = initialize_env(cr)
    policy = VectorPolicy(f32, 4)
    res = numpy.zeros(10, dtype = numpy.float32)
    tape = construct_tape(env, cr)
    f = vectorize_tape(tape, sympy.Symbol('x_0'), sympy.Symbol('x_h'), 4)
    t1 = numpy.array([0,1,4,9],dtype = numpy.float32)
    t2 = numpy.array([16,24,32,40], dtype= numpy.float32)
    t3 = numpy.array([32,32,32,32],dtype = numpy.float32)
    tape = numpy.array([t1,t2,t3], dtype = numpy.float32)

    module = ir.Module(name= "kernel")
    ftype = emit_signature(res, tape)
    func, builder = emit_entry_block(module, ftype, "penguin")
    regs = Registers(builder, policy, 3)
    regs.bind(func, 1)
    regs.prologue(3)
    traces_byorder = partition_orders(env, cr) 
    generate_nested(regs, traces_byorder, env, policy)
    builder.ret_void()
    call = compile_fn(module, "penguin", res.ndim)
    return call

