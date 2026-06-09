from numba import njit, prange
import numpy as np
import time

@njit(parallel=True)
def f_grid(n, arr):
    size = 10**n
    for i in prange(size):
        x = float(i)
        for j in range(size):
            y = float(j)
            arr[i, j] = (
                np.exp(0.25 * x**2 - 0.3 * y**2)
                * np.cos(x**3 + 0.5 * x**2 + 2.0 * x * y - 0.5 * y**4)
                * np.cos(0.7 * x * y**2 - 1.3 * x**2 * y + 0.4 * y**3)
                * np.exp(-0.1 * (x**2 + y**2))
                * np.sin(2.1 * x - 0.6 * y**3 + 0.05 * x**2 * y**2)
            )

N = 3
arr = np.zeros((10**N, 10**N))
f_grid(N, arr)                      # warm up JIT
start = time.perf_counter()
f_grid(N, arr)
end = time.perf_counter()
print(end - start)