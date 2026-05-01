from .cr import *


@CRalgebra.defineUnary(TAN, CRnum)
def tanCRnum(u):
    return CRnum(tan(u.valueof()))

@CRalgebra.defineUnary(TAN, CRsum)
def tanCRsum(u):
    new_operands = [sin(u[i]) if i < len(u) else cos(u[i-len(u)]) for i in range(len(u)*2)]
    return CRtan(new_operands,u.order)

@CRalgebra.defineDefault(TAN)
def defaultTan(u):
    # fallback 
    return CREtan([u.copy()],u.order)



