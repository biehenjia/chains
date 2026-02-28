import pycr,ast, math, numba, numpy, time
expr = "sin(x**2)+x**3"
other, symbol_table = pycr.chainify(expr)
#print(other)

stuff = pycr.chain_ast(expr)
print(ast.unparse(stuff))
f = pycr.compile_ast(stuff)
a = [0] * 10


# warm up
f(a, 0,1, 10)

start = time.perf_counter()
DIM = 1000000
a = numpy.zeros(DIM)
f(a, 0,1,DIM)
end = (time.perf_counter() - start)

a = numpy.zeros(DIM)
s1 = time.perf_counter()
f_numba = numba.njit(f, fastmath=True,nogil=True)
f_numba(a, 0,1,3) # warmup
print(time.perf_counter()- s1)


start = time.perf_counter()
f_numba(a, 0,1,DIM)
end_n = (time.perf_counter() - start)
print(end_n)
print(a[0],a[1],a[-1])

print(end/end_n)



# issue: tower type cr, i.e., CRE class of objects
# does not have reliable eval mode when we use valueof
# e.g

# issue: update propogation, i.e., trig may need to propogate updates
# but trig does not shift itself