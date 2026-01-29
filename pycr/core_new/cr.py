import sympy, math
from algebra import *

CRalgebra = Algebra()

class CR:
    def __init__(self, order, length):
        self.order = order
        self.length = length
    
    def __len__(self):
        return len(self.operands)
    
    def __setitem__(self, key, value):
        self.operands[key] = value

    def __getitem__(self, key):
        return self.operands[key]
    
    def isnumber(self):
        return False
    
    def pop(self):
        return self.operands.pop()
    
    def copy(self):
        res = type(self)(self.order, len(self))
        for i in range(len(self)):
            res[i] = self[i].copy()
        return res
    
    def __add__(self, target):
        if self.order > target.order:
            key = (type(self), CRnum)
        elif self.order < target.order:
            key = (CRnum, type(target))
        else:
            key = (type(self), type(target))
        return CRalgebra.apply(ADD, self, target, key =key)
    
    def __mul__(self, target):
        if self.order > target.order:
            key = (type(self), CRnum)
        elif self.order < target.order:
            key = (CRnum, type(target))
        else:
            key = (type(self), type(target))
        return CRalgebra.apply(ADD, self, target, key =key)

    def __pow__(self, target):
        key = (type(self),type(target))
        return CRalgebra.apply(POW, self, target, key=key)

    def sin(self, target):
        return CRalgebra.apply(SIN, self, key=type(self))

class CRnum(CR):
    # can be numeric: rational, expression, symbolic
    def __init__(self, value):
        # default to sympy value
        if not isinstance(value, sympy.Symbol):
            self.value = sympy.S(value)
        else:
            self.value = value

    def is_zero(self):
        return self.value.is_zero

    def is_one(self):
        return (self.value-1).is_zero

class CRsum(CR):
    def simplify(self):
        result = self.copy()
        j = len(result) - 1
        while (j > 0) and isinstance(self[j], CRnum) and self[j].is_zero():
            result.pop()
        if j == 0:
            return CRnum(0)
        else:
            return result

class CRprod(CR):
    def simplify(self):
        result = self.copy()
        for i in range(len(result)):
            if isinstance(result[i], CRnum) and result[i].is_zero():
                break
        while len(self) > i:
            result.pop()
        
        if len(result) == 0:
            return CRnum(0)

    def correctP(self, newlength):
        result = CRprod(self.order, newlength)
        for i in range(len(self)):
            result[i] = self[i].copy()
        for i in range(len(self),newlength):
            result[i] = CRnum(1)
        return result
    
class CRtrig(CR):
    
    def correctT(self, newlength):
        result = type(self)(self.order, newlength*2)
        for i in range(len(self)//2):
            result[i] = self[i].copy()
            result[i+newlength] = self[i+len(self)//2].copy()
        
        for i in range(len(self)//2, newlength):
            result[i] = CRnum(0)
            result[i+newlength] = CRnum(1)
        return result

    def simplify(self):
        t = len(self)//2
        if isinstance(self[0], CRnum) and self[0].is_zero() and isinstance(self[t],CRnum) and self[t].is_zero():
            return CRnum(0)
        return self.copy()

class CRsin(CRtrig):
    def valueof(self):
        return self[0].valueof()

class CRcos(CRtrig):
    def valueof(self):
        return self[len(self)//2].valueof()

class CRcot(CRtrig):
    def valueof(self):
        return self[len(self)//2].valueof()/self[0].valueof()

class CRtan(CRtrig):
    def valueof(self):
        return self[0].valueof()/self[len(self)//2].valueof()

class CRE(CR):

    def __init__(self, l, r):
        self.l = l 
        self.r = r

class CREadd(CR):
    pass

class CREmul(CR): 
    pass

class CREpow(CR): 
    # TODO: fix
    pass 
    
class CREtrig(CR):
    pass

class CREsin(CREtrig):
    pass 

class CREcos(CREtrig):
    pass 

class CREtan(CREtrig):
    pass


class CREcot(CREtrig):
    pass



def sin(arg):
    if isinstance(arg, sympy.Number):
        return sympy.sin(arg)
    elif isinstance(arg, CR):
        return arg.sin()

def cos(arg):
    if isinstance(arg, sympy.Number):
        return sympy.cos(arg)
    elif isinstance(arg, CR):
        return arg.cos()
    
def tan(arg):
    if isinstance(arg, sympy.Number):
        return sympy.tan(arg)
    elif isinstance(arg, CR):
        return arg.tan()

def cot(arg):
    if isinstance(arg, sympy.Number):
        return 1/sympy.tan(arg)
    elif isinstance(arg, CR):
        return arg.cot()

