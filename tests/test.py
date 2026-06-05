import pycr
import numpy 



s = "x**2"
cr, st = pycr.parse(s)
print(cr)

f = pycr.test_scalar(cr)
res = numpy.zeros(10, dtype=numpy.float32)
tape = numpy.array((0,1,2),dtype=numpy.float32)
print(res.shape, res.dtype, id(res))
f(res, tape)
print(res)