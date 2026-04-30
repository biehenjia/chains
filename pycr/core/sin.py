from .cr import *


@CRalgebra.defineUnary(SIN, CRnum)
def sinCRnum(u):
    return CRnum(sin(u.valueof()))

@CRalgebra.defineUnary(SIN, CRsum)
def sinCRsum(u):
    new_operands = [sin(u[i]) if i < len(u) else cos(u[i]) for i in range(len(u)*2)]
    return CRsin(new_operands,u.order)

@CRalgebra.defineDefault(SIN)
def defaultSin(u):
    # fallback 
    return CREsin([u.copy()],u.order)



