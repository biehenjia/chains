from .crconfig import *
from .dispatch import *
from .generators import *
from .scheduler import *
from .subexpressions import *
from .parallel import dispatch_parallel

def generate_scalar(cr: CR, dtype = numpy.float32, seeding=None, name="penguin"):
    env = initialize_env(cr) # AGNOSTIC
    symbols = extract_symbols(cr) # AGNOSTIC
    policy = ScalarPolicy(f32)
    module = ir.Module(name="kernel") # AGNOSTIC
    # vvvvv kind of agnostic because the x_h doesn't change but x_0 changes, we can throw it into a transformation pipeline
    seeding = seeding or {f"{v.name}_0":0 for v in symbols} | {f"{v.name}_h":1 for v in symbols}
    n_dims = len(symbols) #AGNOSTIC
    dims = list(1 for i in range(n_dims)) #AGNOSTIC
    temp_res = numpy.zeros(dims,dtype=dtype) #AGNOSTICm but requires vectorization support
    tape = construct_tape(env, cr)# AGNOSTIC, but requires an additonal step to parallelize
    tape_np = numpy.array([v.subs(seeding) for v in tape],dtype=dtype) #

    ftype = emit_signature(temp_res, tape_np)
    func,builder = emit_entry_block(module, ftype, name)

    regs = Registers(builder, policy, len(tape))# AGNOSTIC
    regs.bind(func, n_dims) #AGNOSTIC
    regs.prologue(len(tape)) #AGNOSTIC
    traces_byorder = partition_orders(env, cr) #AGNOSTIC
    generate_nested(regs, traces_byorder, env, policy)# AGNOSTIC
    builder.ret_void() #AGNOSTIC

    f = compile_fn(module, name, n_dims) # AGNOSTIC
    return f, tape_np 

def prepare_function(cr: CR, dtype = numpy.float32, policy = LanePolicy, name = "function", parallel = False):
    env = initialize_env(cr)
    prepare_cse(env, cr)
    cr = cse(env, {}, cr)
    env = initialize_env(cr)

    symbols = extract_symbols(cr)

    module = ir.Module(name="kernel")
    n_dims = len(symbols)
    temp_res = numpy.zeros(list(1 for i in range(n_dims)), dtype= dtype)
    tape = construct_tape(env, cr)


    if isinstance(policy, VectorPolicy):
        inner_symbol = max(symbols, key = str)
        tape = vectorize_tape(tape, sympy.Symbol(f"{inner_symbol.name}_0"),sympy.Symbol(f"{inner_symbol}_h"), policy.W)
        tape_np = numpy.zeros((len(tape), policy.W), dtype=dtype)
    else:
        tape_np = numpy.zeros(len(tape), dtype = dtype)
    
    xtape = prepare_tape(tape,{"x_0":0, "x_h":1, "y_0":0, "y_h":1})
    for x in env:
        if isinstance(x, CRnum):
            continue
        cfg = env[x]
        print(x)
        print(xtape[cfg.tape_start:cfg.tape_start+len(x)])

    ftype = emit_signature(temp_res, tape_np)
    func, builder = emit_entry_block(module, ftype, name)
    regs = Registers(builder, policy, len(tape))
    regs.bind(func, n_dims)
    regs.prologue(len(tape))
    traces_byorder = partition_orders(env, cr)
    generate_nested(regs, traces_byorder, env, policy)
    builder.ret_void()
    f = compile_fn(module, name, n_dims)
    return f, tape

def prepare_tape(tape: list[sympy.Expr] | list[list[sympy.Expr]], mapping: dict[str, tuple[float, float]], dtype= numpy.float32):
    if isinstance(tape[0], list):
        # vectorized
        pretape = []
        for entry in tape:
            temp = [v.subs(mapping) for v in entry]
            pretape.append(numpy.array(temp, dtype=dtype))
    else:
        pretape = [v.subs(mapping) for v in tape]
        
    return numpy.array(pretape,dtype = dtype)
    
def prepare_parallel(lowest_variable, tape, bounds,mapping,dtype,  N):
    symbol_0, symbol_h = f"{lowest_variable.name}_0", f"{lowest_variable.name}_h"
    outer_bound = bounds[0]
    
    tapes = []
    offset = 0

    mapping = mapping.copy()
    x0 = mapping[symbol_0]
    xh = mapping[symbol_h]
    for i in range(N):
        mapping[symbol_0] = x0 + i * (outer_bound//N)*xh
        tapes.append(prepare_tape(tape, mapping, dtype))
        # print(tapes[-1])
    return numpy.array(tapes, dtype = dtype)

        