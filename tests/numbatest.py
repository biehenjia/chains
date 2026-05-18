import numba,math,numpy, time

expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"

@numba.njit()
def f(R,X,Y):
    for i in range(X):
        for j in range(Y):
            R[i,j] = math.exp(0.25*i**2-0.3*j**2)*math.cos(0.3*i**3+0.5*i**2+2*i*j-0.5*j**2)
X = 10**3
R = numpy.zeros((X,X),dtype= numpy.float32)

start = time.perf_counter()
f(R,X,X)
print(time.perf_counter()- start)