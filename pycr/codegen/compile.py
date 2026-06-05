import ctypes, numpy
import llvmlite.binding as llvm
from .intrinsics import *



def finalize_module(module: ir.Module, cpu: str= "native", features: str = "+neon"):
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    module.triple = llvm.get_default_triple()
    module.data_layout = llvm.Target.from_default_triple().create_target_machine(cpu=cpu,features=features).target_data


def compile_fn(module, func_name, n_dims, features=""):
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    module.triple = llvm.get_default_triple()
    cpu = llvm.get_host_cpu_name()
    tm = llvm.Target.from_default_triple().create_target_machine(cpu=cpu, features=features)
    module.data_layout = tm.target_data
    llvm_mod = llvm.parse_assembly(str(module))
    llvm_mod.verify()

    pto = llvm.create_pipeline_tuning_options(speed_level=2)
    pb  = llvm.PassBuilder(tm, pto)
    mpm = pb.getModulePassManager()
    mpm.run(llvm_mod, pb)

    engine = llvm.create_mcjit_compiler(llvm_mod, target_machine=tm)
    engine.finalize_object()

    argtypes = [ctypes.c_void_p, ctypes.c_void_p] + [ctypes.c_int64] * n_dims
    cfunc = ctypes.CFUNCTYPE(None, *argtypes)(engine.get_function_address(func_name))

    def call(result_arr, tape_arr):
        print(result_arr.shape, result_arr.dtype, id(result_arr))
        bounds = [ctypes.c_int64(result_arr.shape[i]) for i in range(n_dims)]
        print(f"result ptr: {result_arr.ctypes.data}")
        print(f"tape ptr:   {tape_arr.ctypes.data}")
        print(f"bounds:     {[b.value for b in bounds]}")
        print(f"fn ptr: {engine.get_function_address(func_name)}")
        print(func_name)  # should be exactly "penguin"
        cfunc(
            result_arr.ctypes.data_as(ctypes.c_void_p),
            tape_arr.ctypes.data_as(ctypes.c_void_p),
            *bounds,
        )


    call._engine = engine
    return call