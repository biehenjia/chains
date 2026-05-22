from .cr import *

@CRalgebra.defineBinary(LOG, CRnum, CRnum)
def logCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(sympy.log(l.valueof(), r.valueof()))

@CRalgebra.defineBinary(LOG, CRprod, CRnum)
def logCRprodCRnum(l: CRprod, r: CRnum):
    new_operands = [log(l[i], r) for i in range(len(l))]
    return CRsum(new_operands, l.variable)

@CRalgebra.defineDefault(LOG)
def logDefault(l: CR, r: CR):
    variable = l.variable if l.variable.name > r.variable.name else r.variable
    return CRElog([l.copy(), r.copy()], variable)