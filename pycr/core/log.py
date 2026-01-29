from .cr import *

@CRalgebra.defineBinary(LOG, CRnum, CRnum)
def logCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(sympy.log(l.valueof(), r.valueof()))

@CRalgebra.defineBinary(LOG, CRprod, CRnum)
def logCRprodCRnum(l: CRprod, r: CRnum):
    result = CRsum(l.order, len(l))
    for i in range(len(result)):
        result[i] = log(l[i], r)
    return result

@CRalgebra.defineDefault(LOG)
def logDefault(l: CR, r: CR):
    return CRElog(l, r)