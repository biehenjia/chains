from cr import *

'''
valid additions:
CRnum + CRnum
CRnum + CRsum
CRsum + CRsum

'''

# region: valid additions
@CRalgebra.defineBinary(ADD, CRnum, CRnum,commutative=True)
def addCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(l.valueof() + r.valueof())

@CRalgebra.defineBinary(ADD, CRsum, CRnum, commutative=True)
def addCRsumCRnum(l: CRsum, r: CRnum):
    result = l.copy()
    result[0] += r
    return result

@CRalgebra.defineBinary(ADD, CRsum, CRsum, commutative=True)
def addCRsumCRsum(l: CRsum, r: CRsum):
    if len(r) > len(l):
        l, r = r, l
    result = l.copy()
    for i in range(len(r)):
        result[i] += r[i]
    return result

#endregion


# --- DEFAULTS ---

@CRalgebra.defineDefault(ADD)
def defaultAdd(l, r):
    return CREadd(l,r )





