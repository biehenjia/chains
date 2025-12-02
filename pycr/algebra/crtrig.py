from ..core.engine import *

# region: crtrig
def crtrig_mul(self, target):
    if self > target:
        if type(self) in (CRsin, CRcos):
            result = self.copy()
            result[0] *= target
            result[len(self)//2] *= target
        else:
            return CREmul(self.copy(), target.copy()).simplified()
    elif target > self:
        return target * self
    else:    
        if isinstance(target,CRprod):
            if len(self) // 2 > len(target):
                o1 = self
                o2 = target.correctP(len(self)//2)
                newlength = len(self) // 2
            elif len(self)//2 < len(target):
                o1 = self.correctT(len(target))
                o2 = target
                newlength = len(self) // 2
            else:
                o1 = self
                o2 = target
                newlength = len(self) //2
            result = type(self)(self.order, newlength)
            for i in range(newlength):
                result[i] = o1[i] * o2[i]    
                result[i+newlength] = o1[i+newlength] * o2[i]
            return result
        else:
            return CREmul(self.copy(), target.copy())

def correctT(self,newlength):
    result = type(self)(self.order, newlength * 2)
    for i in range(len(self)//2):
        result[i] = self[i].copy()
        result[i+newlength] = self[i + len(self)//2].copy()
    
    for j in range(len(self)//2,newlength):
        result[i] = CRnum(0)
        result[i + newlength] = CRnum(1)
    return result

CRtrig.__mul__ = crtrig_mul
CRtrig.correctT = correctT
