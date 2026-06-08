import ctypes, numpy
import llvmlite.binding as llvm
from .intrinsics import *

llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

def finalize_module(module: ir.Module, cpu: str= "native", features: str = "+neon"):
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    module.triple = llvm.get_default_triple()
    module.data_layout = llvm.Target.from_default_triple().create_target_machine(cpu=cpu,features=features).target_data

def make_module(module, tm):
    module.triple = llvm.get_default_triple()
    module.data_layout = tm.target_data
    llvm_mod = llvm.parse_assembly(str(module))
    llvm_mod.verify()
    return llvm_mod

def optimize(llvm_mod: llvm.ModuleRef, tm: llvm.TargetMachine, pto=None)->None:
    pto = pto or set_pto()
    pb = llvm.PassBuilder(tm, pto)
    mpm = pb.getModulePassManager()
    mpm.run(llvm_mod, pb)

def jit(llvm_mod: llvm.ModuleRef, tm: llvm.TargetMachine, func_name, n_dims):
    engine = llvm.create_mcjit_compiler(llvm_mod, tm)
    engine.finalize_object()
    llvm.check_jit_execution()
    fn_ptr = engine.get_function_address(func_name)
    argtypes = [ctypes.c_void_p, ctypes.c_void_p] + [ctypes.c_int64] * n_dims
    cfunc = ctypes.CFUNCTYPE(None, *argtypes)(fn_ptr)

    def call(result_arr, tape_arr):
        bounds = [ctypes.c_int64(result_arr.shape[i]) for i in range(n_dims)]
        cfunc( result_arr.ctypes.data_as(ctypes.c_void_p), tape_arr.ctypes.data_as(ctypes.c_void_p), *bounds )
    
    call._engine = engine
    call._cfunc = cfunc 
    return call

def set_pto(speed = 3, vectorize = True) -> llvm.PipelineTuningOptions:
    pto = llvm.create_pipeline_tuning_options(speed)
    pto.loop_interleaving = True
    pto.loop_unrolling = True
    pto.loop_vectorization = vectorize
    pto.slp_vectorization = vectorize
    return pto

def compile_fn(module, func_name, n_dims, cpu=None, features="", pto=None):
    #print(str(module))
    cpu = cpu or llvm.get_host_cpu_name()
    tm  = llvm.Target.from_default_triple().create_target_machine(cpu=cpu, features=features, opt=3)
    pto = pto or set_pto(speed=3, vectorize=True)
    llvm_mod = make_module(module, tm)
    optimize(llvm_mod, tm, pto)
    #print(str(llvm_mod))
    #print(llvm_mod.get_function(func_name)) 
    return jit(llvm_mod, tm, func_name, n_dims)


