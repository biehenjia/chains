from .cr import *

@CRalgebra.defineUnary(COS, CRnum)
def cosCRnum(u): return CRnum(cos(u.valueof()))
@CRalgebra.defineUnary(COS, CRsum)
def cosCRsum(u):
    new_operands = [sin(u[i]) if i < len(u) else cos(u[i-len(u)]) for i in range(len(u)*2)]
    return CRcos(new_operands,u.variable)
@CRalgebra.defineDefault(COS)
def defaultCos(u): return CREcos([u.copy()],u.variable)