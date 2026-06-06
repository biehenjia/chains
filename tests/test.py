import pycr
import numpy 


def run_scalar():
    s = "x**2"
    cr, st = pycr.parse(s)
    print(cr)

    f = pycr.test_scalar(cr)
    res = numpy.zeros(10, dtype=numpy.float32)
    tape = numpy.array((0,1,2),dtype=numpy.float32)
    print(res.shape, res.dtype, id(res))
    f(res, tape)
    print(res)

def run_vectorized():
    s = "x**2+y**2"
    cr, st = pycr.parse(s)
    t1 = numpy.array([0,1,4,9],dtype = numpy.float32)
    t2 = numpy.array([16,24,32,40], dtype= numpy.float32)
    t3 = numpy.array([32,32,32,32],dtype = numpy.float32)
    tape = numpy.array([t1,t2,t3], dtype = numpy.float32)

    f = pycr.test_vector(cr)
    res = numpy.zeros(10, dtype= numpy.float32)
    f(res,tape)
    print(res)

run_vectorized()