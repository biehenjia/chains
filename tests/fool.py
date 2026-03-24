import numba, numpy, time


@numba.njit( fastmath=True)
def T(A, X,Y):
    for i in range(X):
        i2 = i**2
        for j in range(Y):
            A[i, j] = i2 + j**2

def T_numpy(A, X, Y):
    i = numpy.arange(X)
    j = numpy.arange(Y)
    A[:X, :Y] = (i**2)[:, None] + (j**2)[None, :]


0.000525
0.00022

0.00068

A = numpy.zeros((1,1))
T(A,1,1)
X = Y= 10000

A = numpy.zeros((X,Y))
start = time.perf_counter()
T(A, X,Y)
end = time.perf_counter()

print(end-start)


