import ctypes
import llvmlite.binding as llvm
from llvmlite import ir

_initialized = False

def _initialize() -> None:
    global _initialized
    if _initialized:
        return
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    _initialized = True

_initialize()


def make_target_machine(cpu: str | None = None, features: str = "", opt: int = 3) -> llvm.TargetMachine:
    cpu = cpu or llvm.get_host_cpu_name()
    return llvm.Target.from_default_triple().create_target_machine(cpu=cpu, features=features, opt=opt)


def set_pto(speed: int = 3, vectorize: bool = True) -> llvm.PipelineTuningOptions:
    pto = llvm.create_pipeline_tuning_options(speed)
    pto.loop_interleaving = True
    pto.loop_unrolling = True
    pto.loop_vectorization = vectorize
    pto.slp_vectorization = vectorize
    return pto


def parse_module(module: ir.Module, tm: llvm.TargetMachine) -> llvm.ModuleRef:
    module.triple = llvm.get_default_triple()
    module.data_layout = tm.target_data
    llvm_mod = llvm.parse_assembly(str(module))
    llvm_mod.verify()
    return llvm_mod


def optimize(llvm_mod: llvm.ModuleRef, tm: llvm.TargetMachine, pto: llvm.PipelineTuningOptions | None = None) -> None:
    pto = pto or set_pto()
    pb = llvm.PassBuilder(tm, pto)
    pb.getModulePassManager().run(llvm_mod, pb)


def jit_link(llvm_mod: llvm.ModuleRef, tm: llvm.TargetMachine, func_name: str, n_dims: int):
    engine = llvm.create_mcjit_compiler(llvm_mod, tm)
    engine.finalize_object()
    llvm.check_jit_execution()
    fn_ptr = engine.get_function_address(func_name)
    argtypes = [ctypes.c_void_p, ctypes.c_void_p] + [ctypes.c_int64] * n_dims
    cfunc = ctypes.CFUNCTYPE(None, *argtypes)(fn_ptr)

    def call(result_arr, tape_arr):
        bounds = [ctypes.c_int64(result_arr.shape[i]) for i in range(n_dims)]
        cfunc(
            result_arr.ctypes.data_as(ctypes.c_void_p),
            tape_arr.ctypes.data_as(ctypes.c_void_p),
            *bounds,
        )

    call._engine = engine
    call._cfunc = cfunc
    return call


def compile_fn(module: ir.Module, func_name: str, n_dims: int, cpu: str | None = None, features: str = "", pto=None):
    tm = make_target_machine(cpu=cpu, features=features)
    llvm_mod = parse_module(module, tm)
    optimize(llvm_mod, tm, pto)
    return jit_link(llvm_mod, tm, func_name, n_dims)
