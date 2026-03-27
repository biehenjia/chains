# save as test_novec.py - run as fresh python process
import llvmlite.binding as llvm
llvm.set_option('', '--disable-loop-vectorization')
llvm.set_option('', '--disable-slp-vectorization')

# NOW import numba
from numba import njit, prange
import numpy as np
import time


from numba import njit, prange

@njit(parallel=True, fastmath=True)
def T(A, B_0, B_1):
    TILE = 48
    n_tiles_i = (B_0 + TILE - 1) // TILE  # ceiling division
    n_tiles_j = (B_1 + TILE - 1) // TILE

    for ti in prange(n_tiles_i):          # prange with step=1
        for tj in range(n_tiles_j):
            for i in range(ti * TILE, min(ti * TILE + TILE, B_0)):
                for j in range(tj * TILE, min(tj * TILE + TILE, B_1)):
                    A[i, j] = float(i*i + j*j)

A = np.empty((1000, 1000))
T(A, 1000, 1000)  # warmup

# verify
asm = T.inspect_asm(T.signatures[0])
lines = asm.split('\n')
print("stp count:", sum(1 for l in lines if 'stp' in l))
print("str count:", sum(1 for l in lines if '\tstr\t' in l))

# benchmark
times = []
for _ in range(200):
    t = time.perf_counter()
    T(A, 1000, 1000)
    times.append(time.perf_counter() - t)

times.sort()
print(f"median: {times[100]*1000:.3f}ms")
print(f"min:    {times[0]*1000:.3f}ms")