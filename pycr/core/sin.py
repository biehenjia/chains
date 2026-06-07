from .cr import *


@CRalgebra.defineUnary(SIN, CRnum)
def sinCRnum(u):
    return CRnum(sin(u.valueof()))

@CRalgebra.defineUnary(SIN, CRsum)
def sinCRsum(u):
    new_operands = [sin(u[i]) if i < len(u) else cos(u[i-len(u)]) for i in range(len(u)*2)]
    return CRsin(new_operands,u.variable)

@CRalgebra.defineDefault(SIN)
def defaultSin(u):
    # fallback 
    return CREsin([u.copy()],u.variable)



