from algebraic import *

POW = Operator.POW

@CRalgebra.defineBinary(POW, CRnum, CRnum)
def powCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(l.valueof() ** r.valueof())

@CRalgebra.defineBinary(POW, CRsum, CRnum)
def powCRsumCRnum(l: CRsum, r: CRnum):
    pass 

@CRalgebra.defineBinary(POW, CRnum, CRsum)
def powCRnumCRsum(l: CRnum, r: CRsum):
    result = CRprod(r.order, len(r))
    for i in range(len(result)):
        result[i] = l ** r[i]
    return result



@CRalgebra.defineBinary(POW, CRprod, CRnum)
def powCRprodCRnum(l: CRprod, r: CRnum):
