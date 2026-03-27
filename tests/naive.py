import llvmlite.binding as llvm
llvm.set_option('', '--disable-loop-vectorization')
llvm.set_option('', '--disable-slp-vectorization')
from numba import njit
import numpy, time
print('hi')

@njit()
def T(A, X,Y):
    for i in range(X):
        i2 = i**2
        for j in range(Y):
            A[i,j] = i2 + j**2



0.000525
0.00022

0.00068


A = numpy.zeros((1,1))
T(A,1,1)
X = Y= 1000

sig = list(T.signatures)[0]
asm = list(T.inspect_asm().values())[0]

first_fn_end = asm.find('__ZN7cpython')
print(asm[:first_fn_end])
# # print(asm)



A = numpy.zeros((X,Y))
start = time.perf_counter()
T(A, X,Y)
end = time.perf_counter()

print(end-start)


