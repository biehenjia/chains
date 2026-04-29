from numba import njit
import numpy as np

@njit
def f():
    out = np.empty(10_000)
    for i in range(10_000):
        out[i] = i ** 6
    return out

f()
print(list(f.inspect_llvm().values())[0])