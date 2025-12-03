from cr import *

class Algebra:

    def __init__(self):
        
        self.uTable = {}
        self.bTable = {}
        self.commutesTable = {}

    def defineUnary(self, operator, uType):

        def registrar(fn):
            self.uTable[operator][uType] = fn
            return fn
        return registrar
    
    def defineBinary(self, operator, lType, rType, commutative=False):
        
        self.commutesTable[operator] = commutative
        def registrar(fn):
            self.binaryTable[operator][(lType, rType)] = fn
            return fn
        return registrar
    
    
    def apply(self, operator, *args):
        if len(args) == 1:
            return self.applyUnary(operator, args[0])
        elif len(args) == 2:
            return self.applyBinary(operator, args[0], args[1])
        else:
            raise ValueError("????")
    
    def applyUnary(self, operator, u):
        table = self.unaryTable.get(operator, {})
        fn = table.get(type(u))
        if fn is None:
            raise NotImplementedError(f"{operator} not defined on {type(u)}")
        return fn(u)
    
    def applyBinary(self, operator, l,r ):
        table = self.binaryTable.get(operator,{})
        key = (type(l),type(r))
        fn = table.get(key)
        if fn is None and self.commutesTable.get(operator, False):
            key = (type(r),type(l))
            fn = table.get(key)
            if fn is not None:
                return fn(r,l)
        
        if fn is None:
            raise NotImplementedError(f"{operator} not defined on {type(l)} and {type(r)}")
        
        return fn(l,r)

