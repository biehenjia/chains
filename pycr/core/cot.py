from .cr import *

@CRalgebra.defineDefault(COT)
def defaultCot(u):
    return CREcot([u.copy()],u.order)

@CRalgebra.defineUnary(COT)
def cotCRnum(u):
    return CRnum(cot(u.valueof()))

@CRalgebra.defineUnary(COT, CRsum)
def cotCRsum(u):
    new_operands = [sin(u[i]) if i < len(u) else cos(u[i]) for i in range(len(u)*2)]
    return CRtan(new_operands,u.order)


