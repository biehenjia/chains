import math, sys, hashlib
import struct
from .algebraic import *
EPSILON = sys.float_info.epsilon
PROTOCOL = hashlib.blake2b

algebra = CRalgebra #...?

class CR:
    def __init__(self, order, length):
        self.order = order 
        self.operands = [None for i in range(length)]
        self.digested = None

        self.dependencies = set()
    
    
    def __len__(self):
        return len(self.operands)
    
    def __setitem__(self, key, value):
        self.operands[key] = value
    
    def __getitem__(self, key):
        return self.operands[key]

    def pop(self):
        return self.operands.pop()

    def __str__(self):
        layers = [f"{self.__class__.__name__}({self.valueof(),self.order})"]
        for i,node in enumerate(self):
            layers.extend(node.walk_str("",i== len(self)-1))
        return "\n".join(layers)
    
    def walk_str(self,prefix="", terminal=True):
        pipe = "└─ " if terminal else "├─ "
        layer = f"{prefix}{pipe}{self.__class__.__name__}({self.valueof(),self.order})"
        layers = [layer]
        prefix_c = f"{prefix}{'   ' if terminal else '|  '} "
        for i,node in enumerate(self):
            layers.extend(node.walk_str(prefix_c,i == len(self)-1 ))
        return layers
    
    def isnumber(self):
        return False

    def copy(self):
        res = type(self)(self.order, self.length)
        for i in range(len(self)):
            res[i] = self[i].copy()
        return res
    
    def __hash__(self):
        pass 

    def crdigest(self):
        if not self.digested is None:
            return self.digested
        h = PROTOCOL(digest_size=16)
        h.update(type(self).__name__.encode())

        for cr in self:
            h.update(cr.crdigest())
        self.digested = h.digest()
        return self.digested


class CRsum(CR):
    def simplify(self):
        result = self.copy()
        j = len(result) -1 
        while (j > 0) and isinstance(self[j], CRnum) and result[j].iszero():
            result.pop()
            j -= 1
        if j == 0:
            return CRnum(0)
        else:
            return result
    
    def __add__(self, target):
        if self > target:
            key = (type(self), CRnum)
        elif self < target:
            key = (CRnum, type(target))
        else:
            key = (type(self), type(target))
        return CRalgebra.apply(ADD, self, target, key=key)

    def seed(self, start, step):
        a = CRnum(start)
        b = CRnum(step)
        self.operands[0] = a
        self.operands[1] = b

class CRnum(CR):
    def __init__(self, value):
        self.value = value

    def isnumber(self):
        return True
    
    def copy(self):
        return CRnum(self.value)
    
    def valueof(self):
        return self.value

    def simplify(self):
        return self.copy()
    
    def iszero(self):
        return abs(self.value) < EPSILON
    
    def isone(self):
        return abs(self.value - 1) < EPSILON

    def crdigest(self):
        if not self.digested is None:
            return self.digested
        h = PROTOCOL(digest_size=16)
        h.update(type(self).__name__.encode())

        if isinstance(self.value, float):
            if math.isnan(self.value):
                h.update(b"NAN")
            else:
                h.update(b"F")
                h.update(struct.pack("!d", self.value))
        else:
            h.update(repr(self.value).encode())
        
        self.digested = h.digest()
        return self.digested
    
    def isinteger(self):
        return isinstance(self.value, int) or (isinstance(self.value, float) and self.value.is_integer())


    
class CRprod(CR):
    def simplify(self):
        result = self.copy()
        for i in range(len(result)):
            if isinstance(result[i], CRnum) and result[i].iszero():
                break
        while len(self) > i:
            result.pop()
        
        if len(result) == 0:
            return CRnum(0)
        elif len(result) == len(self):
            j = len(result) - 1
            while j > 0 and isinstance(result[j],CRnum) and result[j].isone():
                result.pop()
                j -= 1
            if len(result) == 0:
                return CRnum(1)
            else:
                return result
    
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
        if isinstance(self[0], CRnum) and self[0].iszero() and isinstance(self[t],CRnum) and self[t].iszero():
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
    
    def crdigest(self):
        if not self.digested is None:
            return self.digested
        
        h = PROTOCOL(digest_size=16)
        h.update(type(self).__name__.encode())

        sdigests = sorted(cr.digest() for cr in self)
        for s in sdigests:
            h.update(s)
        self.digested = h.digest()
        return self.digested
    


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



    
