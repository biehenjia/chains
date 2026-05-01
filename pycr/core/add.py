from .cr import *

@CRalgebra.defineBinary(ADD, CRnum, CRnum,commutative=True)
def addCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(l.valueof() + r.valueof())

@CRalgebra.defineBinary(ADD, CRsum, CRnum, commutative=True)
def addCRsumCRnum(l: CRsum, r: CRnum):

    new_operands = [l[i] for i in range(len(l))]
    new_operands[0] += r
    return CRsum(new_operands, l.order)

@CRalgebra.defineBinary(ADD, CRsum, CRsum, commutative=True)
def addCRsumCRsum(l: CRsum, r: CRsum):
    if len(r) > len(l):
        l, r = r, l
    new_operands = [l[i] + r[i] if i < len(r) else l[i] for i in range(len(l))]
    return CRsum(new_operands, l.order)

@CRalgebra.defineDefault(ADD)
def defaultAdd(l, r):
    return CREadd([l.copy(), r.copy()], max(l.order,r.order))





