from .cr import *


@CRalgebra.defineDefault(SIN)
def defaultSin(u):
    return CREsin(u)

@CRalgebra.defineUnary(SIN, CRnum)
def sinCRnum(u):
    return CRnum(sin(u.valueof()))

@CRalgebra.defineUnary(SIN, CRsum)
def sinCRsum(u):
    result = CRtrig(len(u)*2)
    for i in range(len(u)):
        result[i] = sin(u[i])
        result[i+len(u)] = cos(u[i])
    return result


