from ..core.engine import *

def crprod_mul(self, target):
    """
    multiplication of two CR's
    """
    # case: self order is greater, multiply the constant term
    if self > target:
        result = self.copy()
        result[0] *= target
        return result.simplified()
    # case: target order is greater, obey invariant
    elif target > self:
        return target * self
    # case: orders are the same, invoke special case.
    else:
        if isinstance(target, CRprod):
            minlength = min(len(self), len(target))
            result = self.copy() if len(self) > len(target) else target.copy()
            for i in range(minlength):
                # multiply componentwise, extend the longer chain.
                result[i] = self[i] * target[i]
            return result.simplified
        else:
            return CREmul(self.copy(), target.copy()).simplified()

def crprod_pow(self, target ):
    if self > target or self < target:
        result = self.copy()
        for i in range(len(self)):
            result[i] **= target
        return result.simplified()
    # case: order of target is greater, obey invariant.
    # case: orders are the same
    else:
        # case: crprod^crsum; invoke CRpow algorithm
        if isinstance(target, CRsum):
            newlength = len(self) + len(target)  -1

            result = CRsum(self.order, len(self))
            
            if len(self) > len(target) :
                m = len(self) - 1
                n = len(target ) - 1 
            else:
                m = len(target ) - 1
                n = len(self) - 1 
            
            # count
            for i in range(newlength):
                r1 = CRnum(1)
                bound11 = max(0, i-m)
                bound12 = min(i, n)
                
                #count1
                for j in range(bound11,bound12):
                    r2 = CRnum(1)
                    bound21 = max(i - j,0)
                    bound22 = min(j, m)
                    
                    #count2
                    for k in range(bound21,bound22+1):
                        temp1 = target[k] * CRnum(math.comb(j,i-k))
                        temp2 = temp1  * CRnum(math.comb(i,j))
                        temp3 = self[j] ** temp2
                        r2 *= temp3  
                    r1 *= r2
                
                result[i] = r1.copy()
                return result.simplified()
        else:
            return CREpow(self.copy(), target.copy())

def crprod_log(self):
    result = CRsum(self.order, len(self))
    for i in range(len(self)):
        result[i] = self[i].ln()
    return result.simplified()

def crprod_correctP(self,newlength):
    result = CRprod(self.order, newlength)
    for i in range(len(self)):
        result[i] = self[i].copy()
    for i in range(len(self),newlength):
        result[i] = CRnum( 1)
    return result

CRprod.__mul__ = crprod_mul
CRprod.__pow__ = crprod_pow
CRprod.log = crprod_log
CRprod.correctP = crprod_correctP