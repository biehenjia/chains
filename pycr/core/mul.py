from .cr import *

'''
valid multiplications:
CRnum * CRnum  
CRsum * CRnum 
CRsum * CRsum
CRprod * CRprod
CRprod * CRnum
CRprod * CRtrig
'''

@CRalgebra.defineBinary(MUL, CRnum, CRnum, commutative=True)
def mulCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(l.valueof() * r.valueof())

@CRalgebra.defineBinary(MUL, CRsum, CRnum, commutative=True)
def mulCRsumCRnum(l: CRsum, r: CRnum):
    operands = [l[i] * r for i in range(len(l))]
    return CRsum(operands, l.variable)

@CRalgebra.defineBinary(MUL, CRsum, CRsum, commutative=True)
def mulCRsumCRsum(l: CRsum, r: CRsum):
    if len(r) > len(l):
        l, r = r,l
    n = len(l) - 1
    m = len(r) - 1
    operands = [None for i in range(n+m+1)]
    for i in range(n+m+1):
        r1 = CRnum(0)
        for j in range(max(0,i-m),min(i,n)+1):
            r2 = CRnum(0)
            for k in range(i-j,min(i,m)+1):
                r2 += CRnum(sympy.binomial(j,i-k)) * r[k]
            r2 *= CRnum(sympy.binomial(i,j))

            r1 += l[j] * r2
        operands[i] = r1
    return CRsum(operands, l.variable)

@CRalgebra.defineBinary(MUL, CRprod, CRprod, commutative=True)
def mulCRprodCRprod(l: CRprod, r: CRprod):
    if len(r) > len(l): l, r = r, l
    operands = [l[i] * r[i] if i < len(r) else l[i] for i in range(len(l))]
    return CRprod(operands, l.variable)

@CRalgebra.defineBinary(MUL, CRprod, CRnum, commutative=True)
def mulCRprodCRnum(l: CRprod, r: CRnum):
    operands = [l[i] for i in range(len(l))]
    operands[0] *= r
    return CRprod(operands, l.variable)

# CASES FOR SIN AND COS

#TODO: fix mul case for 
@CRalgebra.defineBinary(MUL, CRprod, CRcos, commutative=True)
def mulCRprodCRtrig(l: CRprod, r: CRcos):
    if len(r)//2 > len(l):
        o1 = r
        o2 = l.correctP(len(r)//2)
        newlength = len(r)//2
    elif len(r)//2 < len(l):
        o1 = r.correctT(len(l))
        o2 = l
        newlength = len(l)//2
    else:
        o1 = r
        o2 = l
        newlength = len(r)//2
    new_operands = [o1[i]*o2[i] if i < newlength else o1[i] * o2[i-newlength] for i in range(newlength*2)]
    return CRcos(new_operands,r.variable)

#TODO: fix mul case for 
@CRalgebra.defineBinary(MUL, CRprod, CRsin, commutative=True)
def mulCRprodCRtrig(l: CRprod, r: CRsin):
    if len(r)//2 > len(l):
        o1 = r
        o2 = l.correctP(len(r)//2)
        newlength = len(r)//2
    elif len(r)//2 < len(l):
        o1 = r.correctT(len(l))
        o2 = l
        newlength = len(l)//2
    else:
        o1 = r
        o2 = l
        newlength = len(r)//2
    
    new_operands = [o1[i]*o2[i] if i < newlength else o1[i] * o2[i-newlength] for i in range(newlength*2)]
    return CRsin(new_operands,r.variable)

@CRalgebra.defineBinary(MUL, CRsin, CRnum, commutative=True)
def mulCRsinCRnum(l: CRsin, r: CRnum):
    new_operands = [l[i] for i in range(len(l))]
    new_operands[0] *= r
    new_operands[len(l)//2] *= r
    return CRsin(new_operands, l.variable)

@CRalgebra.defineBinary(MUL, CRcos, CRnum, commutative=True)
def mulCRcosCRnum(l: CRcos, r: CRnum):
    new_operands = [l[i] for i in range(len(l))]
    new_operands[0] *= r
    new_operands[len(l)//2] *= r
    return CRcos(new_operands, l.variable)


# --- DEFAULTS ---


@CRalgebra.defineDefault(MUL)
def defaultMul(l, r):
    variable = l.variable if l.variable.name > r.variable.name else r.variable
    return CREmul([l.copy(), r.copy()], variable)

