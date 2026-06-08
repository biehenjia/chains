import ctypes
from concurrent.futures import ThreadPoolExecutor 
import numpy, llvmlite.binding as llvm, llvmlite.ir as ir

llvm.initialize_native_target()
llvm.initialize_all_asmprinters()

_pool : ThreadPoolExecutor | None = None

def get_pool(n):
    global _pool 
    if _pool is None:
        _pool = ThreadPoolExecutor(max_workers=n)
    return _pool

def dispatch_parallel(call, result: numpy.ndarray, tape_batch: numpy.ndarray, bounds: list[int]):
    cfunc = call._cfunc
    N = tape_batch.shape[0]
    outer = bounds[0]
    inner = result.size// outer
    itemsize = result.itemsize
    chunk = outer// N
    counts = [chunk] * N
    counts[-1] += outer% N
    starts = [sum(counts[:i]) for i in range(N)]

    inner_bounds = [ctypes.c_int64(b) for b in bounds[1:]]

    def run(i):
        r = ctypes.c_void_p(result.ctypes.data + starts[i] * inner * itemsize)
        t = ctypes.c_void_p(tape_batch[i].ctypes.data )
        cfunc(r,t, ctypes.c_int64(counts[i]), *inner_bounds)
    pool = get_pool(N)
    futures = [pool.submit(run,i) for i in range(N)]
    for f in futures:
        f.result()