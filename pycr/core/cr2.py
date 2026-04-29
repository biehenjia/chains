from dataclasses import dataclass
import sympy, hashlib, struct
from . import algebra
from operator import add, mul, pow

CRalgebra = algebra.Algebra()


@dataclass(frozen=True)
class CR:

    operands: tuple[CR, ...]
    order: int

    def __init__(self, operands, order): 
        self.operands = operands
        self.order = order
        

    def __len__(self):
        return len(self.operands) 
    
    def __getitem__(self, key):
        return self.operands[key]
    
    def postorder(self):
        for operand in self.operands:
            yield from operand.postorder()
        yield self

    def copy(self):
        new_operands = tuple([self[i].copy() for i in range(len(self))])
        return type(self)(new_operands, self.order)
    
    def __add__(self,target):
        if self.order > target.order:
            key = (type(self), CRnum)
        elif self.order < target.order:
            key = (CRnum, type(target))
        else:
            key = (type(self, type(target)))
        return CRalgebra.apply(algebra.ADD, self, target , key=key)
    
    def __mul__(self, target):
        if self.order > target.order:
            key = (type(self), CRnum)
        elif self.order < target.order:
            key = (CRnum, type(target))
        else:
            key = (type(self, type(target)))
        return CRalgebra.apply(algebra.MUL, self, target, key=key)

    def __pow__(self, target):
        key = (type(self),type(target))
        return CRalgebra.apply(algebra.POW, self, target, key=key)
    
    def sin(self):
        return CRalgebra.apply(algebra.SIN, self, key=type(self))

    def cos(self):
        return CRalgebra.apply(algebra.COS, self, key=type(self))

    def tan(self):
        return CRalgebra.apply(algebra.TAN, self, key=type(self))
    
    def cot(self):
        return CRalgebra.apply(algebra.COT, self, key=type(self))
    
    def log(self, target=None):
        if target is None:
            target = CRnum(sympy.E)
        key = (type(self), type(target))
        return CRalgebra.apply(algebra.LOG, self, target, key=key)
    
    def __str__(self):
        layers = [f"{self.__class__.__name__}({self.order})"]
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
    
    def valueof(self):
        return self[0].valueof()

@dataclass(frozen=True)
class CRnum(CR):
    
    value: sympy.Basic

    def __init__(self, value):
        if not isinstance(value, sympy.Symbol):
            self.value = (sympy.S(str(value), rational=True),)
        else:
            self.value = (value,)
        self.order = -1

    def postorder(self):
        yield self

    def valueof(self):
        return self.value[0]
    
    def simplify(self):
        return self
    
    def copy(self):
        return CRnum(self.valueof())
    
    def is_integer(self):
        return self.valueof().is_Integer

    def is_zero(self):
        return self.valueof().is_zero
    
    def is_one(self):
        return (self.valueof() -1).is_zero

    def crhash(self):
        h = hashlib.blake2b()
        h.update(b"CRnum")
        h.update(str(self.value).encode())
        return h.digest()
    
    def walk_str(self, prefix="", terminal=True):
        return [f"{prefix}{'└─ ' if terminal else '├─ '}CRnum({self.value})"]

@dataclass(frozen=True)
class CRsum(CR):
    
    operands: tuple[CR, ...]
    order: int

    def simplify(self):
        j = len(self)-1
        while j > 0 and isinstance(self[j], CRnum) and self[j].is_zero():
            j -= 1
        if j == 0:
            return CRnum(0)
        new_operands = tuple([self[i].copy() for i in range(j)])
        return CRsum(new_operands, self.order)
        

class CRprod(CR):
    
    operands: tuple[CR, ...]
    order: int

    def simplify(self):
        # first instance of 0, nothing beyond it will change
        for i in range(len(self)):
            if isinstance(self[i], CRnum) and self[i].is_zero():
                break
        while i > 0 and isinstance(self[i], CRnum) and self[i].is_one():
            i -= 1
        if i == 0:
            return CRnum(1)
        new_operands = tuple([self[j].copy() for j in range(i)])
        return CRprod(new_operands, self.order)
    
    def correctP(self, newlength):
        new_operands = tuple([self[i].copy() if i < len(self) else CRnum(1) for i in range(newlength)])
        return CRprod(new_operands, self.order)

        

class CRtrig(CR):
    operands: tuple[CR, ... ]
    order: int

    def correctT(self, newlength):
        hl = len(self)//2
        left = tuple([self[i].copy() if i < hl else CRnum(0) for i in range(len(self))])
        right = tuple([self[i+hl].copy() if i < hl else CRnum(1) for i in range(len(self))])
        new_operands = left+ right
        return CRtrig(new_operands,self.order, self.crtype)
    
    def simplify(self):
        hl = len(self)//2
        if isinstance(self[0],CRnum) and self[0].is_zero() and isinstance(self[hl],CRnum) and self[hl].is_zero():
            return CRnum(0)
        return self
    
@dataclass(frozen=True)
class CRsin(CRtrig):

    def valueof(self):
        return self.operands[0]
    
@dataclass(frozen=True)
class CRcos(CRtrig):

    def valueof(self):
        return self.operands[len(self)//2]
    

@dataclass(frozen=True)
class CRtan(CRtrig):

    def valueof(self):
        return self.operands[0]/ self.operands[len(self)//2]
    
@dataclass(frozen=True)
class CRcot(CRtrig):

    def valueof(self):
        return  self.operands[len(self)//2]/ self.operands[0]

@dataclass(frozen = True)    
class CRE(CR):
    operands: tuple[CR, ...]
    order: int
    crtype: int

    


    
    





def sin(arg):
    if isinstance(arg, sympy.Expr):
        return sympy.sin(arg)
    elif isinstance(arg, CR):
        return arg.sin()

def cos(arg):
    if isinstance(arg, sympy.Expr):
        return sympy.cos(arg)
    elif isinstance(arg, CR):
        return arg.cos()
    
def tan(arg):
    if isinstance(arg, sympy.Expr):
        return sympy.tan(arg)
    elif isinstance(arg, CR):
        return arg.tan()

def cot(arg):
    if isinstance(arg, sympy.Expr):
        return 1/sympy.tan(arg)
    elif isinstance(arg, CR):
        return arg.cot()

def log(arg, base = None):
    if isinstance(arg, sympy.Expr):
        if base is None:
            base = sympy.E
        return sympy.log(arg, base)
    elif isinstance(arg, CR):
        if base is None:
            base = CRnum(sympy.E)
        return arg.log(base) 