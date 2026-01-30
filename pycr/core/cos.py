from .cr import *

@CRalgebra.defineUnary(COS, CRnum)
def cosCRnum(u):
    return CRnum(cos(u.valueof()))

@CRalgebra.defineUnary(COS, CRsum)
def cosCRsum(u):
    result = CRcos(order=u.order, length=len(u)*2)
    for i in range(len(u)):
        result[i] = sin(u[i])
        result[i+len(u)] = cos(u[i])
    return result

@CRalgebra.defineDefault(COS)
def defaultCos(u):
    # fallback 
    return CREcos(u )
