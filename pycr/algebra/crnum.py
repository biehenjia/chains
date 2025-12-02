from engine import *

# region: crnum
def crnum_add(self, target):
    if target > self:
        return target + self
    elif isinstance(target, CRnum):
        return CRnum(self.value + target.value)

def crnum_mul(self, target):
    if target > self:
        return target * self
    elif isinstance(target, CRnum):
        return CRnum(self.value * target.value)
    
def crnum_pow(self, target):
    if isinstance(target, CRsum):
        result =  CRprod(target.order, len(target))
        for i in range(len(target)):
            result[i] = self ** target[i]
        return result
    elif isinstance(target, CRnum):
        return CRnum(self.value ** target.value)
    else:
        return CREpow(self.copy(), target.copy())


def crnum_sin(self):
    return CRnum(sin(self.value))

def crnum_cos(self):
    return CRnum(cos(self.value))

def crnum_cot(self):
    return CRnum(1 / tan(self.value))

def crnum_tan(self):
    return CRnum(tan(self.value))

def crnum_log(self):
    return CRnum(log(self.value))

def crnum_exp(self):
    return CRnum(exp(self.value))

CRnum.__add__ = crnum_add
CRnum.__mul__ = crnum_mul
CRnum.__pow__ = crnum_pow

CRnum.sin = crnum_sin
CRnum.cos = crnum_cos
CRnum.cot = crnum_cot
CRnum.tan = crnum_tan
CRnum.log = crnum_log
CRnum.exp = crnum_exp