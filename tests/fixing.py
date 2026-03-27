import numba,numpy, time

from numba import llvmlite
@numba.njit(fastmath = True)
def T(A, B0, B1):
    r0 = 0
    r1 = 1
    r2 = 2
    r3 = 0
    r4 = 0 
    r5 = 1
    r6 = 2
    r7 = 0
    for i in range(B0):
        r0 += r1
        r1 += r2
        r3 = r0
        for j in range(B1):
            A[i][j] = r7

            r4 += r5
            r5 += r6
            r7 = r4
        r4 = 0
        r5 = 1
        r6 = 2

        r4 = r3
        r7 = r4

X = 10000
Y = 10000
A = numpy.zeros((X,Y))

T(numpy.zeros((5,5)),1,1)
start = time.perf_counter()
T(A,X,Y)
end = time.perf_counter()
print(end-start)
