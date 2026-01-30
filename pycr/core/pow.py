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
                base *= base
            return result

        else:
            raise NotImplementedError("NEGATIVE CRSUM EXPONNENTS NOD DONE")
    else:
        raise NotImplementedError("NON-INTEGER CRSUM EXPONNENTS NOT DONE")


@CRalgebra.defineBinary(POW, CRnum, CRsum)
def powCRnumCRsum(l: CRnum, r: CRsum):
    result = CRprod(r.order, len(r))
    for i in range(len(result)):
        result[i] = l ** r[i]
    return result

@CRalgebra.defineBinary(POW, CRprod, CRnum)
def powCRprodCRnum(l: CRprod, r: CRnum):
    result = CRprod(l.order, len(l))
    for i in range(len(result)):
        result[i] = l[i] ** r
    return result

@CRalgebra.defineBinary(POW, CRprod,CRsum)
def powCRprodCRsum(l: CRprod, r: CRsum):
    n = max(len(l),len(r)) - 1
    m = min(len(l),len(r)) - 1
    result = CRprod(l.order, n+m+1)
    
    for i in range(len(result)):
        r1 = CRnum(1)
        for j in range(max(0,i-m),min(i,n)+1):
            r2 = CRnum(1)
            for k in range(i-j,min(i,m)+1):
                r2 *= l[j] ** r[k] * CRnum(sympy.binomial(j,i-k)*sympy.binomial(i,j))
            r1 *= r2
        result[i] = r1
    return result.simplify()


# --- DEFAULTS ---
@CRalgebra.defineDefault(POW)
def defaultPow(l, r):
    return CREpow(l,r )