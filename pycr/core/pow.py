import sympy
from .cr import *

'''
Types: CRnum, CRsum, CRprod, CRtrig
Total: (4 + 2 - 1) choose 2 = 10 combinations

CRnum ^ CRnum: done
CRnum ^ CRsum: done
CRprod ^ CRnum: done

CRsum ^ CRnum (positive integer): done
CRsum ^ CRnum (negative integer): not done
CRsum ^ CRnum (non-integer): not done

CRtrig ^ CRnum
'''

@CRalgebra.defineBinary(POW, CRnum, CRnum)
def powCRnumCRnum(l: CRnum, r: CRnum):
    return CRnum(l.valueof() ** r.valueof())

@CRalgebra.defineBinary(POW, CRsum, CRnum)
def powCRsumCRnum(l: CRsum, r: CRnum):

    if r.is_integer():
        result = CRnum(1)
        if r.valueof() >= 0:
            v = int(r.valueof())
            base = l.copy()
            while v > 0:
                if v & 1:
                    result *= base
                v >>= 1
                if v > 0:
                    base *= base
            return result

        else:
            
            raise NotImplementedError("NEGATIVE CRSUM EXPONNENTS NOD DONE")
    else:
        return CREpow(l, r)
        # raise NotImplementedError("NON-INTEGER CRSUM EXPONNENTS NOT DONE")


@CRalgebra.defineBinary(POW, CRnum, CRsum)
def powCRnumCRsum(l: CRnum, r: CRsum):
    new_operands = [l ** r[i] for i in range(len(r))]
    return CRprod(new_operands, r.variable)

@CRalgebra.defineBinary(POW, CRprod, CRnum)
def powCRprodCRnum(l: CRprod, r: CRnum):
    new_operands = [l[i]** r for i in range(len(l))]
    return CRprod(new_operands, l.variable)

@CRalgebra.defineBinary(POW, CRprod,CRsum)
def powCRprodCRsum(l: CRprod, r: CRsum):
    n = max(len(l),len(r)) - 1
    m = min(len(l),len(r)) - 1
    new_operands = [None for i in range(n+m+1)]
    for i in range(len(new_operands)):
        r1 = CRnum(1)
        for j in range(max(0,i-m),min(i,n)+1):
            r2 = CRnum(1)
            for k in range(i-j,min(i,m)+1):
                r2 *= l[j] ** r[k] * CRnum(sympy.binomial(j,i-k)*sympy.binomial(i,j))
            r1 *= r2
        new_operands[i] = r1
    return CRprod(new_operands, l.variable)


# --- DEFAULTS ---
@CRalgebra.defineDefault(POW)
def defaultPow(l, r):
    variable = l.variable if l.variable.name > r.variable.name else r.variable
    return CREpow([l.copy(), r.copy()], variable)