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

def dispatch_parallel(call, result, tape_batch, bounds):
    cfunc = call._cfunc
    N = tape_batch.shape[0]
    outer = bounds[0]
    assert outer % N == 0, (
        f"dispatch_parallel requires outer bound ({outer}) divisible by N ({N}); "
        "chunk assignment will overlap or skip otherwise."
    )
    inner = result.size // outer
    result_stride = inner * result.itemsize
    tape_stride = tape_batch.strides[0]
    result_base = result.ctypes.data
    tape_base = tape_batch.ctypes.data
    inner_bounds = tuple(bounds[1:])

    chunk, rem = divmod(outer, N)
    args = []
    offset = 0
    for i in range(N):
        cnt = chunk + (1 if i < rem else 0)
        args.append((
            result_base + offset * result_stride,
            tape_base + i * tape_stride,
            cnt,
            *inner_bounds,
        ))
        offset += cnt

    pool = get_pool(N)
    futures = [pool.submit(cfunc, *args[i]) for i in range(N - 1)]
    cfunc(*args[-1])
    for f in futures:
        f.result()