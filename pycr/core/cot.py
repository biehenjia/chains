from .cr import *

@CRalgebra.defineDefault(TAN)
def defaultTan(u):
    return CREtan(u)

@CRalgebra.defineUnary(TAN, CRnum)
def tanCRnum(u):
    return CRnum(tan(u.valueof()))

@CRalgebra.defineUnary(TAN, CRsum)
def tanCRsum(u):
    result = CRcot(len(u)*2)
    for i in range(len(u)):
        result[i] = tan(u[i])
        result[i+len(u)] = tan(u[i+len(u)])
    return result

