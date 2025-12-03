from algebra import *

CRalgebra = Algebra()

# canonical ordering is Num, Sum, Prod, Trig, CREs

@CRalgebra.defineBinary(Operator.ADD, CRnum, CRsum, commutative=True)
def addCRnumCRsum(l : CRnum, r: CRsum ):
    result = r.copy()
    result[0] += l
    return result

@CRalgebra.defineBinary(Operator.ADD, CRsum, CRsum, commutative = True)
def addCRsumCRsum(l: CRsum, r: CRsum):

    if l < r:
        result = l.copy()
        result[0] += r
        return result
    elif r < l:
        result = r.copy()
        result[0] += l
        return result
    else:
        if len(l) < len(r):
            l,r = r,l
        result = l.copy()
        for i in range(len(r)):
            result[i] += r[i]
        return result

@CRalgebra.defineBinary(Operator.ADD, CRnum, CRnum, commutative = True)
def addCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(l.valueof() + r.valueof())



@CRalgebra.defineBinary(Operator.MUL, CRnum, CRnum, commutative = True)
def mulCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(l.valueof() * r.valueof())

@CRalgebra.defineBinary(Operator.MUL, CRnum, CRsum, commutative = True)
def mulCRnumCRsum(l: CRnum, r: CRsum):
    result = r.copy()
    for i in range(len(result)):
        result[i] *= l
    return result

@CRalgebra.defineBinary(Operator.MUL, CRsum, CRsum, commutative=True)
def mulCRsumCRsum(l: CRsum, r: CRsum):
    if l > r:
        result = l.copy()
        result[0] *= r
        return result
    if r < l:
        result = r.copy()
        result[0] *= l
        return result
    else:
        
