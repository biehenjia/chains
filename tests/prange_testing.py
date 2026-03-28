import numpy, time
import numba 

@numba.njit(parallel=True)
def generated(A, x_0, x_h, y_0, y_h, B_0, B_1, n_threads):
    chunk = B_0 // n_threads
    for t in numba.prange(n_threads):
        K = t * chunk
        x_0 = K
        r_0 = R_0 = x_0 ** 2 + y_0 ** 2
        r_1 = R_1 = x_0 * x_h + x_h * (x_0 + x_h)
        r_2 = R_2 = 2 * x_h ** 2
        r_3 = R_3 = x_0 ** 2 + y_0 ** 2
        r_4 = R_4 = x_0 ** 2 + y_0 ** 2
        r_5 = R_5 = y_0 * y_h + y_h * (y_0 + y_h)
        r_6 = R_6 = 2 * y_h ** 2
        r_7 = R_7 = x_0 ** 2 + y_0 ** 2
        UL = B_0 if t == n_threads - 1 else K + chunk
        for L_0 in range(K, UL):
            r_0 += r_1
            r_1 += r_2
            r_3 = r_0
            for L_1 in range(B_1):
                A[L_0, L_1] = r_7
                r_4 += r_5
                r_5 += r_6
                r_7 = r_4
            r_4 = R_4
            r_5 = R_5
            r_6 = R_6
            r_4 = r_3
            r_7 = r_4

X = Y = 10000
A = numpy.zeros((X,Y))
generated(numpy.zeros((1,1)),0,1,0,1,1,1,4)
start = time.perf_counter()
generated(A,0,1,0,1,X,Y,4)
end = time.perf_counter()
print(end-start )
# print(A)