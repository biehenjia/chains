import pycr, llvmlite
import numpy, math
expr = "x**2+y**2"
cr, _ = pycr.chainify(expr,vectorized=True)
# print(cr)
st = {'x_0':0, 'x_h':1, 'y_0': 0, 'y_h':1}
ncr = cr.seeded(st)



term = pycr.CRterm(ncr)
term.cr = pycr.cse({},term.cr)

# print(term.cr)

f = pycr.compile_cr_vec(term, llvmlite.ir.FloatType(), W=4 )
print("___")
for thing in term.tape:
    print(thing)
print(f.ir_opt)
# X = 4
# import time
# res = numpy.zeros((X,X),dtype=numpy.float32)
# start = time.perf_counter()
# f(res, X,X)
# print(time.perf_counter() - start)
# for row in res:
#     print(row)
# import numba,math,numpy, time

# expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"

# @numba.njit()
# def f(R,X,Y):
#     for i in range(X):
#         for j in range(Y):
#             R[i,j] = math.exp(0.25*i**2-0.3*j**2)*math.cos(0.3*i**3+0.5*i**2+2*i*j-0.5*j**2)
# X = 10**3
# R = numpy.zeros((X,X),dtype= numpy.float32)

# start = time.perf_counter()
# f(R,X,X)
# print(time.perf_counter()- start)

# print(numpy.abs(res-R).max())