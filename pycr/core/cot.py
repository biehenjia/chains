from .cr import *

@CRalgebra.defineDefault(COT)
def defaultCot(u): return CREcot([u.copy()],u.variable)

@CRalgebra.defineUnary(COT, CRnum)
def cotCRnum(u): return CRnum(cot(u.valueof()))

@CRalgebra.defineUnary(COT, CRsum)
def cotCRsum(u):
    new_operands = [sin(u[i]) if i < len(u) else cos(u[i-len(u)]) for i in range(len(u)*2)]
    return CRcot(new_operands,u.variable)


