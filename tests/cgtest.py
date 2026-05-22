import pycr, llvmlite
import numpy, math
# expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"
# cr, _ = pycr.chainify(expr,vectorized=True)
# # print(cr)
# st = {'x_0':0, 'x_h':0.001, 'y_0': 0, 'y_h':0.001}
# ncr = cr.seeded(st)



# term = pycr.CRterm(ncr)
# term.cr = pycr.cse({},term.cr)

# # print(term.cr)

# f = pycr.compile_cr_vec(term, llvmlite.ir.FloatType(), W=4 )
# # print("___")
# # for thing in term.tape:
# #     print(thing)
# # print(f.ir_opt)
# X = 10**4
# import time
# res = numpy.zeros((X,X),dtype=numpy.float32)
# start = time.perf_counter()
# f(res, X,X)
# print(time.perf_counter() - start)


# print(res)
import numba,math,numpy, time

expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"

@numba.njit()
def f(R,X,Y):
    x = 0.0
    for i in range(X):
        x += 1.0

        for j in range(Y):
            pass
X = 10**4
R = numpy.zeros((X,X),dtype= numpy.float32)

f(R,X,X)

start = time.perf_counter()
f(R,X,X)
print(time.perf_counter()- start)

asm = list(f.inspect_asm().values())[0]
print(asm)