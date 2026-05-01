from .cr import *

@CRalgebra.defineUnary(COS, CRnum)
def cosCRnum(u):
    return CRnum(cos(u.valueof()))

@CRalgebra.defineUnary(COS, CRsum)
def cosCRsum(u):
    new_operands = [sin(u[i]) if i < len(u) else cos(u[i-len(u)]) for i in range(len(u)*2)]
    for thing in new_operands: 
        print(type(thing))
    return CRcos(new_operands,u.order)

@CRalgebra.defineDefault(COS)
def defaultCos(u):
    # fallback 
    return CREcos([u.copy()],u.order)
