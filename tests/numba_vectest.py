import numba as nb
import numpy as np

@nb.njit(parallel=True, fastmath=True, cache=True)
def kernel(x, y, out):
    nx, ny = x.shape[0], y.shape[0]
    for i in nb.prange(nx):
        xi = x[i]
        xi2 = xi * xi
        xi3 = xi2 * xi
        a = 0.3 * xi3 + 0.5 * xi2
        ex_x = 0.25 * xi2
        for j in range(ny):
            yj = y[j]
            yj2 = yj * yj
            e = ex_x - 0.3 * yj2
            c = a + 2.0 * xi * yj - 0.5 * yj2
            out[i, j] = np.exp(e) * np.cos(c)


x = np.linspace(-2.0, 2.0, 1000)
y = np.linspace(-2.0, 2.0, 1000)
out = np.empty((1000, 1000))
kernel(x, y, out)