import sympy, hashlib, struct
from __future__ import annotations
from .algebra import *
from operator import add, mul, pow
CRalgebra = Algebra()

class CR:
    
    operands: list["CR"]
    variable: sympy.Symbol 

    def __init__(self, operands, variable): 
        self.operands = operands
        self.variable = variable

    def __len__(self): return len(self.operands) 
    def __getitem__(self, key): return self.operands[key]

    
    def postorder(self):
        for operand in self.operands:
            yield from operand.postorder()
        yield self

    def copy(self):
        new_operands = [self[i].copy() for i in range(len(self))]
        return type(self)(new_operands, self.variable)
    
    def isnumber(self):
        return False

    # returns a copy of the cr but elements are replaced with realized values
    def seeded(self, symbol_table):
        return type(self)([self[i].seeded(symbol_table) for i in range(len(self))], self.variable)                    
            
    
    def __add__(self,target: CR) -> CR:
        if self.variable.name > target.variable.name:
            key = (type(self), CRnum)
        elif target.variable.name < target.variable.name:
            key = (CRnum, type(target))
        else:
            key = (type(self), type(target))
        return CRalgebra.apply(ADD, self, target , key=key)
    
    def __mul__(self, target: CR) -> CR:
        if self.variable.name > target.variable.name:
            key = (type(self), CRnum)
        elif self.variable.name < target.variable.name:
            key = (CRnum, type(target))
        else:
            key = (type(self), type(target))
        return CRalgebra.apply(MUL, self, target, key=key)

    def __pow__(self, target):
        key = (type(self),type(target))
        return CRalgebra.apply(POW, self, target, key=key)
    
    def sin(self): return CRalgebra.apply(SIN, self, key=type(self))
    def cos(self): return CRalgebra.apply(COS, self, key=type(self))
    def tan(self): return CRalgebra.apply(TAN, self, key=type(self))
    def cot(self): return CRalgebra.apply(COT, self, key=type(self))
    
    def log(self, target=None):
        if target is None:
            target = CRnum(sympy.E)
        key = (type(self), type(target))
        return CRalgebra.apply(LOG, self, target, key=key)
    
    def __str__(self):
        layers = [f"{self.__class__.__name__}({self.variable})"]
        for i,node in enumerate(self):
            layers.extend(node.walk_str("",i== len(self)-1))
        return "\n".join(layers)
    
    def walk_str(self,prefix="", terminal=True):
        pipe = "└─ " if terminal else "├─ "
        layer = f"{prefix}{pipe}{self.__class__.__name__}({self.valueof(),self.variable})"
        layers = [layer]
        prefix_c = f"{prefix}{'   ' if terminal else '|  '} "
        for i,node in enumerate(self):
            layers.extend(node.walk_str(prefix_c,i == len(self)-1 ))
        return layers
    
    def valueof(self):
        return self[0].valueof()
    
    def _suffixhash(self):
        # works for both CRsum and CRprod types
        # need to account for the same order
        # should also just work with the CRE types
        prev = f"{type(self)}({self.variable})".encode()
        suffix_hashes = [None for i in range(len(self))]
        for i in range(len(self)):
            h = hashlib.blake2b()
            h.update(prev)
            h.update(self[-i-1].crhash())
            h.update(b"|")
            suffix_hashes[-i-1] = h.digest()
            prev = suffix_hashes[-i-1]
        return suffix_hashes
        
    
    def crhash(self):
        if not hasattr(self, "suffix_hashes"):
            self.suffix_hashes = self._suffixhash()
        return self.suffix_hashes[0]

class CRnum(CR):

    def __init__(self, value):
        if not isinstance(value, sympy.Symbol):
            self.value = sympy.S(str(value), rational=True)
        else:
            self.value = value
        self.variable = sympy.Symbol('')
    
    def seeded(self, table):
        return CRnum(self.value.subs(table))

    def postorder(self): yield self
    def valueof(self): return self.value
    def simplify(self): return self
    def copy(self): return CRnum(self.valueof())
    def is_integer(self): return self.valueof().is_Integer
    def is_zero(self): return self.valueof().is_zero
    def is_one(self): return (self.valueof() -1).is_zero
    def isnumber(self): return True
    
    def walk_str(self, prefix="", terminal=True):
        return [f"{prefix}{'└─ ' if terminal else '├─ '}CRnum({self.value})"]

    def __str__(self):
        return f"CRnum({self.value})"
    
    def _suffixhash(self):
        h = hashlib.blake2b()
        h.update(b"CRnum")
        h.update(sympy.srepr(self.value).encode())
        return [h.digest()]
    

class CRsum(CR):
    def simplify(self):
        j = len(self)-1
        while j > 0 and isinstance(self[j], CRnum) and self[j].is_zero():
            j -= 1
        if j == 0:
            return CRnum(0)
        new_operands = [self[i].copy() for i in range(j)]
        return CRsum(new_operands, self.variable)



class CRprod(CR):
    def simplify(self):
        # first instance of 0, nothing beyond it will change
        for i in range(len(self)):
            if isinstance(self[i], CRnum) and self[i].is_zero():
                break
        while i > 0 and isinstance(self[i], CRnum) and self[i].is_one():
            i -= 1
        if i == 0:
            return CRnum(1)
        new_operands = [self[j].copy() for j in range(i)]
        return CRprod(new_operands, self.variable)
    
    def correctP(self, newlength):
        new_operands = [self[i].copy() if i < len(self) else CRnum(1) for i in range(newlength)]
        return CRprod(new_operands, self.variable)

        

class CRtrig(CR):
    def correctT(self, newlength):
        hl = len(self)//2
        left = [self[i].copy() if i < hl else CRnum(0) for i in range(len(self))]
        right = [self[i+hl].copy() if i < hl else CRnum(1) for i in range(len(self))]
        new_operands = left+ right
        return CRtrig(new_operands,self.variable)
    
    def simplify(self):
        hl = len(self)//2
        if isinstance(self[0],CRnum) and self[0].is_zero() and isinstance(self[hl],CRnum) and self[hl].is_zero():
            return CRnum(0)
        return self
    
    def _suffixhash(self):
        prev = f"{CRtrig.__name__}({self.variable})".encode()
        suffix_hashes = [None for i in range(len(self)//2)]
        for i in range(len(self)//2):
            h = hashlib.blake2b()
            h.update(prev)
            h.update(self[-i-1].crhash())
            h.update(self[len(self)//2-i-1].crhash())
            h.update(b"|")
            suffix_hashes[len(self)//2 -i- 1] = h.digest()
            prev = suffix_hashes[len(self)//2-i-1]
        return suffix_hashes




    
class CRsin(CRtrig):
    def valueof(self): return self.operands[0].valueof()
    
class CRcos(CRtrig):
    def valueof(self): return self.operands[len(self)//2].valueof()
    
class CRtan(CRtrig):
    def valueof(self): return self.operands[0].valueof()/ self.operands[len(self)//2].valueof()
    
class CRcot(CRtrig):
    def valueof(self): return  self.operands[len(self)//2].valueof()/ self.operands[0].valueof()

class CRE(CR):
    def __init__(self, operands, variable):
        super().__init__(operands, variable)
        least_variable = sympy.Symbol('\U0010ffff')
        for operand in operand:
            if operand.variable.name < least_variable.name:
                least_variable = operand.variable
        self.least_variable = least_variable 

    def realize(self): 
        return [operand.valueof() for operand in self]


# necessary?? already in position to use ops table + lambda/f lookup
class CREadd(CRE):
    def valueof(self): return add(*(self.realize()))
    
class CREmul(CRE):
    def valueof(self): return mul(*(self.realize()))
    
class CREpow(CRE):
    def valueof(self): return pow(*(self.realize()))

class CRElog(CRE):
    def valueof(self): return log(*(self.realize()))

class CREsin(CRE):
    def valueof(self): return sin(*(self.realize()))

class CREcos(CRE):
    def valueof(self): return cos(*(self.realize()))

class CREtan(CRE):  
    def valueof(self): return tan(*(self.realize()))

class CREcot(CRE):
    def valueof(self): return cot(*(self.realize()))

# shouldn't even have a source. It will be a child node of a CRobject
class CREconnector(CRE):
    
    def __init__(self, source, index = -1):
        self.operands = [source]
        self.index = index
        self.variable = source.variable
        self.f_valueof = None

    def valueof(self):
        if self.index == -1:
            return self.operands[0].valueof()
        else:
            return self.operands[0][self.index].valueof()
    
    def crhash(self):
        if not hasattr(self.operands[0], "suffix_hashes"):
            self.operands[0].suffix_hashes = self.operands[0]._suffixhash()
        return self.operands[0].suffix_hashes[self.index] 

def sin(arg):
    if isinstance(arg, sympy.Expr): return sympy.sin(arg)
    elif isinstance(arg, CR): return arg.sin()

def cos(arg):
    if isinstance(arg, sympy.Expr): return sympy.cos(arg)
    elif isinstance(arg, CR): return arg.cos()
    
def tan(arg):
    if isinstance(arg, sympy.Expr): return sympy.tan(arg)
    elif isinstance(arg, CR): return arg.tan()

def cot(arg):
    if isinstance(arg, sympy.Expr): return 1/sympy.tan(arg)
    elif isinstance(arg, CR): return arg.cot()

def log(arg, base = None):
    if isinstance(arg, sympy.Expr):
        if base is None: base = sympy.E
        return sympy.log(arg, base)
    elif isinstance(arg, CR):
        if base is None: base = CRnum(sympy.E)
        return arg.log(base) 


