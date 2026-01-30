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
    result = l.copy()
    for i in range(len(result)):
        result[i] *= r
    return result

@CRalgebra.defineBinary(MUL, CRsum, CRsum, commutative=True)
def mulCRsumCRsum(l: CRsum, r: CRsum):
    if len(r) > len(l):
        l, r = r,l
    n = len(l) - 1
    m = len(r) - 1
    result = CRsum(l.order, n+m+1)
    for i in range(len(result)):
        r1 = CRnum(0)
        for j in range(max(0,i-m),min(i,n)+1):
            r2 = CRnum(0)
            for k in range(i-j,min(i,m)+1):
                r2 += CRnum(sympy.binomial(j,i-k)) * r[k]
            r2 *= CRnum(sympy.binomial(i,j))
            r1 += l[j] * r2
        result[i] = r1
    return result

@CRalgebra.defineBinary(MUL, CRprod, CRprod, commutative=True)
def mulCRprodCRprod(l: CRprod, r: CRprod):
    if len(r) > len(l):
        l, r = r, l
    result = l.copy()
    for i in range(len(result)):
        result[i] *= r[i]
    return result

@CRalgebra.defineBinary(MUL, CRprod, CRnum, commutative=True)
def mulCRprodCRnum(l: CRprod, r: CRnum):
    result = l.copy()
    result[0] *= r
    return result

@CRalgebra.defineBinary(MUL, CRprod, CRtrig, commutative=True)
def mulCRprodCRtrig(l: CRprod, r: CRtrig):
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
    result = type(r)(r.order, newlength*2)
    for i in range(newlength):
        result[i] = o1[i] * o2[i]
        result[i+newlength] = o1[i+newlength] * o2[i]
    return result

@CRalgebra.defineBinary(MUL, CRsin, CRnum, commutative=True)
def mulCRsinCRnum(l: CRsin, r: CRnum):
    result = l.copy()
    result[0] *= r
    result[len(result)//2] *= r
    return result

@CRalgebra.defineBinary(MUL, CRcos, CRnum, commutative=True)
def mulCRcosCRnum(l: CRcos, r: CRnum):
    result = l.copy()
    result[0] *= r
    result[len(result)//2] *= r
    return result



# --- DEFAULTS ---


@CRalgebra.defineDefault(MUL)
def defaultMul(l, r):
    return CREmul(l,r )

