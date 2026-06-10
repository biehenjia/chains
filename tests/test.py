import pycr
import numpy

cr = pycr.parse("x")
cr2 = cr ** pycr.CRnum(2) + pycr.CRnum(2) * cr 

fn = pycr.compile(cr2, dtype = numpy.float32)
bound = fn.bind(x=(0,1,100))
bound()
out = bound.result
