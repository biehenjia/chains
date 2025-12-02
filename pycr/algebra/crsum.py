from ..core.engine import *

def crsum_add(self, target):
    """
    add function 
    
    """
    # case: treat it as a constant. Add it to the constant term
    if self > target:
        result = self.copy()
        # recall: the constant term could also be a CRobject. 
        result[0] = self[0] + target
        result.simplify()
        return result
    # case: target order is greater; obey invariant
    elif target > self:
        return target + self
    # case : two orders are the same.
    # CRsum add is componentwise addition
    else:
        # special case: two CRsums: add componentwise
        if isinstance(target, CRsum):
            minlength = min(len(self),len(target))
            result = self.copy() if len(self) > len(target) else target.copy()
            for i in range(minlength):
                result[i] = self[i] + target[i]
            result.simplify()
            return result
        else:
            # no simplification rules for now
            return CREadd(self.copy(), target.copy()).simplified()

def crsum_mul(self, target):
    """
    
    """
    # case: treat as if it is a constant
    if self > target:
        result = self.copy()
        for i in range(len(self)):
            result[i] *= target
        result.simplify()
        return result
    # case: target is greater; obey invariant
    elif target > self:
        return target * self
    # case : orders are the same
    else:
        # there's only rule for CRsum mul CRsum
        if isinstance(target,CRsum):
            if len(self) >= len(target):
                newlength = len(self) + len(target) - 1
                result = CRsum(order = self.order, length = newlength)
                m = len(target)-1 
                n = len(self) - 1
                for i in range(newlength):
                    r1 = CRnum(value=0)
                    ibound11 = max(i-m,0)
                    ibound12 = min(i,n)
                    for j in range(ibound11, ibound12+1):
                        r2 = CRnum(value =0)
                        ibound21 = max(i-j,0)   
                        ibound22 = min(i,m)
                        for k in range(ibound21,ibound22 + 1):
                            rtemp1 = CRnum(math.comb(j,i-k))
                            rtemp11 = target[k].copy()
                            rtemp1 = rtemp11 * rtemp1
                            r2 = rtemp1 + r2
                        rtemp2 = CRnum(math.comb(i,j))
                        r2 *= rtemp2
                        rtemp2 = self[j] * r2
                        r1 = r1 + rtemp2
                    result[i] = r1.copy()
                result.simplify()
                return result
            else:
                return target * self
        else:
            return CREmul(self.copy(), target.copy()).simplified()

def crsum_pow(self, target):
    if isinstance(target,CRnum):
        result = CRnum(value=1)
        v = abs(target.valueof())
        if v == int(v):
            if v > 0:
                v = int(v)
                base = self.copy()
                while v > 0:
                    if v & 1:
                        result *= base 
                    v //=2 
                    base *= base
                return result.simplified()
            else:
                # negative integer exponent
                v = -int(v)
                base = self.copy()
                while v > 0:
                    if v & 1:
                        result *= base 
                    v //=2 
                    base *= base
                return (CRnum(1) / result).simplified()
        # target does not have integer value; can't raise to power
        else:
            return CREpow(self.copy(), target.copy())
    # target is not CRnum, no valid rules for CRnum^...
    else:
        return CREpow(self.copy(), target.copy())

def crsum_sin(self):
    result = CRsin(self.order, len(self) * 2)
    for i in range(len(self)):
        result[i] = self[i].sin()
        result[i+ len(self) ] = self[i].sin()
    return result.simplified()

def crsum_cos(self):
    result = CRcos(self.order, len(self) * 2)
    for i in range(len(self)):
        result[i] = self[i].sin()
        result[i+ len(self) ] = self[i].cos()
    return result.simplified()

def crsum_tan(self):
    result = CRtan(self.order, len(self))
    for i in range(len(self)):
        result[i] = self[i].sin()
        result[i+ len(self) ] = self[i].cos()
    return result.simplified()

def crsum_cot(self):
    result = CRcot(self.order, len(self))
    for i in range(len(self)):
        result[i] = self[i].sin()
        result[i+ len(self) ] = self[i].cos()
    return result.simplified()


def crsum_exp(self):
    result = CRprod(self.order, len(self))
    for i in range(len(self)):
        result[i] = result[i].exp()
    return result.simplified()


CRsum.__add__ = crsum_add
CRsum.__mul__ = crsum_mul
CRsum.__pow__ = crsum_pow
CRsum.sin = crsum_sin
CRsum.cos = crsum_cos
CRsum.tan = crsum_tan
CRsum.cot = crsum_cot
CRsum.exp = crsum_exp
# endregion
