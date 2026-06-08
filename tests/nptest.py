import numpy,time

def r2_grid(n, arr):
    sq = numpy.arange(10**n, dtype=numpy.float32) ** 6
    numpy.add.outer(sq, sq, out =  arr)

arr = numpy.zeros((10**4, 10**4), dtype =numpy.float32)

start = time.perf_counter()
r2_grid(4, arr)
end = time.perf_counter()
print(end - start)

