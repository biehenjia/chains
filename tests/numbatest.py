from numba import njit, prange
import numpy as np
import time

@njit(parallel=True)
def f_grid(n, arr):
    coords = np.arange(10**n, dtype=np.float64)
    exp_x = np.exp(0.25 * coords ** 2)
    exp_y = np.exp(-0.3 * coords ** 2)
    fx    = 0.3 * coords ** 3 + 0.5 * coords ** 2
    gy    = -0.5 * coords ** 2

    for i in prange(len(coords)):
        for j in range(len(coords)):
            arr[i, j] = exp_x[i] * exp_y[j] * np.cos(fx[i] + 2.0 * coords[i] * coords[j] + gy[j])
N = 3
arr = np.zeros((10**N,10**N))

start = time.perf_counter()
f_grid(N,arr )
end = time.perf_counter()
print(arr)