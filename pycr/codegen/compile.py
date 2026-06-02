from llvmlite import ir, binding
from .emit import emit_function
from .policy import VectorPolicy
from ..core import CRsum, CRprod, CRtrig
import ctypes, math, numpy as np, os
from math import prod
from concurrent.futures import ThreadPoolExecutor

binding.initialize_native_target()
binding.initialize_native_asmprinter()


def _build_engine(module, opt):
    llmod = binding.parse_assembly(str(module))
    llmod.verify()
    tm = binding.Target.from_default_triple().create_target_machine()
    pto = binding.PipelineTuningOptions()
    pto.opt_level = opt
    pto.loop_vectorization = True
    pb = binding.PassBuilder(tm, pto)
    pm = pb.getModulePassManager()
    pm.run(llmod, pb)
    engine = binding.create_mcjit_compiler(llmod, tm)
    engine.finalize_object()
    return engine, llmod, tm


def _ctype_and_dtype(policy):
    if isinstance(policy.scalar_type, ir.FloatType):
        return ctypes.c_float, np.float32
    return ctypes.c_double, np.float64


def _make_cfn_wrapper(engine, llmod, tm, name, plan, policy, ir_unopt):
    csc, dt = _ctype_and_dtype(policy)
    n = len(plan.orders)
    cft = ctypes.CFUNCTYPE(None, ctypes.POINTER(csc), *([ctypes.c_int64] * n))
    raw = cft(engine.get_function_address(name))

    def cfn(arr, *bounds):
        raw(arr.ctypes.data_as(ctypes.POINTER(csc)), *[ctypes.c_int64(b) for b in bounds])

    cfn._engine = engine
    cfn._module = llmod
    cfn.ir_unopt = ir_unopt
    cfn.ir_opt = str(llmod)
    cfn.asm = tm.emit_assembly(llmod)
    cfn.W = policy.W
    return cfn



def _scalar_val(entry): return float(entry[0]) if isinstance(entry, (list, tuple)) else float(entry)


def _advance_cr_slots(node, slots, lo):
    if isinstance(node, CRsum):
        n = len(slots)
        binom = [1.0]
        for j in range(1, n):
            binom.append(binom[-1] * (lo - j + 1) / j)
        return [sum(binom[j] * slots[k + j] for j in range(n - k)) for k in range(n)]

    elif isinstance(node, CRprod):
        n = len(slots)
        if n == 2:
            a, b = slots
            return [a * b**lo, b]
        elif n == 3:
            a, b, c = slots
            return [a * b**lo * c**(lo * (lo - 1) // 2), b * c**lo, c]
        else:
            cur = list(slots)
            for _ in range(lo):
                for i in range(n - 1):
                    cur[i] *= cur[i + 1]
            return cur

    elif isinstance(node, CRtrig):
        t = len(slots) // 2
        if t == 2:
            s0, sh, c0, ch = slots
            angle = math.atan2(s0, c0) + lo * math.atan2(sh, ch)
            return [math.sin(angle), sh, math.cos(angle), ch]
        else:
            cur = list(slots)
            for _ in range(lo):
                new = list(cur)
                for i in range(t - 1):
                    new[i]     = cur[i] * cur[t + i + 1] + cur[t + i] * cur[i + 1]
                    new[t + i] = cur[t + i] * cur[t + i + 1] - cur[i] * cur[i + 1]
                cur = new
            return cur

    return list(slots)


def _seed_tape_flat(plan, lo):
    tape = plan.tape
    result = [_scalar_val(entry) for entry in tape]
    for e in plan.orders[0]:
        slots = [_scalar_val(tape[e.start + i]) for i in range(e.length)]
        seeded = _advance_cr_slots(e.node, slots, lo)
        for i, v in enumerate(seeded): result[e.start + i] = v
    return result



def compile_cr_unified(plan, policy, name="generated", opt=3):
    module = ir.Module(name="crmod")
    module.triple = binding.get_default_triple()
    emit_function(module, name, plan, policy)
    ir_unopt = str(module)
    engine, llmod, tm = _build_engine(module, opt)
    return _make_cfn_wrapper(engine, llmod, tm, name, plan, policy, ir_unopt)


def compile_cr_parallel(plan, policy, name="generated_par", opt=3):
    module = ir.Module(name="crmod_chunk")
    module.triple = binding.get_default_triple()
    chunk_name = name + "_chunk"
    emit_function(module, chunk_name, plan, policy, seed_arg=True)
    engine, llmod, tm = _build_engine(module, opt)

    csc, dt = _ctype_and_dtype(policy)
    n = len(plan.orders)
    tape_n = len(plan.tape)
    # Signature: (float* out, float* seed, int64 B0_chunk, int64 B1, ...)
    cft = ctypes.CFUNCTYPE(None, ctypes.POINTER(csc), ctypes.POINTER(csc), *([ctypes.c_int64] * n))
    raw = cft(engine.get_function_address(chunk_name))
    n_threads = int(os.environ.get("OMP_NUM_THREADS", os.cpu_count() or 1))
    def cfn(arr, *bounds):
        B0 = bounds[0]
        size = (B0 + n_threads - 1) // n_threads
        rest = [ctypes.c_int64(b) for b in bounds[1:]]
        outer_stride = prod(bounds[1:]) if len(bounds) > 1 else 1
        flat = arr.ravel()

        def run(lo):
            seed_vals = _seed_tape_flat(plan, lo)
            seed_arr = (csc * tape_n)(*seed_vals)
            seed_p = ctypes.cast(seed_arr, ctypes.POINTER(csc))
            chunk_size = min(size, B0 - lo)
            out_p = flat[lo * outer_stride:].ctypes.data_as(ctypes.POINTER(csc))
            raw(out_p, seed_p, ctypes.c_int64(chunk_size), *rest)

        with ThreadPoolExecutor(max_workers=n_threads) as ex:
            futs = [ex.submit(run, lo) for lo in range(0, B0, size)]
            for f in futs:
                f.result()

    cfn._engine = engine
    cfn.W = policy.W
    return cfn
