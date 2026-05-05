from llvmlite import ir, binding

f64 = ir.DoubleType()
i64 = ir.IntType(64)
f64_ptr = ir.PointerType(f64)


def generate(ir_object):
    ir_object.prepare()

    # technically, we should already be seeded so its just a matter of ordering.
    n_dims = len(ir_object.st)
    # results array,
    arg_types = [f64_ptr] + [f64] * (2*n_dims) + [i64]* n_dims

    module = ir.Module(name="generated_module")
    fn_type = ir.FunctionType(ir.VoidType(), arg_types)
    fn = ir.Function(module, fn_type, name="generated")

    arg_names = ["A"]
    for sym in ir_object.st:
        start, step = ir_object.st[sym]["params"]
        arg_names += [str(start), str(step)]
    arg_names += [f"B_{i}" for i in range(n_dims)]
    for arg,name in zip(fn.args, arg_names):
        arg.name = name
    
    entry = fn.append_basic_block("entry")
    builder = ir.IRBuilder(entry)
    builder.ret_void()

    return module

    