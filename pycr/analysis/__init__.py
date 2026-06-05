from .crconfig import *
from .dispatch import *
from .generators import *
from .scheduler import *
from .subexpressions import *

def test_scalar(cr: CR):
    env = initialize_env(cr)
    policy = ScalarPolicy(f32)

    res = numpy.zeros(10,dtype=numpy.float32)
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



