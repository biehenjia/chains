

ADD = 'ADD'
MUL = 'MUL'
POW = 'POW'
DIV = 'DIV'

SIN = 'SIN'
COS = 'COS'
TAN = 'TAN'
COT = 'COT'

EXP = 'EXP'
LOG = 'LOG'



class Algebra:

    def __init__(self):
        # unary and binary operators
        self.uTable = {}
        self.bTable = {}
        # binary operators with different orders
        self.commutesTable = {}
        self.defaultTable = {}

    def defineUnary(self, operator, uType):
        if operator not in self.uTable:
            self.uTable[operator] = {}
        def registrar(fn):
            self.uTable[operator][uType] = fn
            return fn
        return registrar
    
    def defineBinary(self, operator, lType, rType, commutative=False):
        if operator not in self.bTable:
            self.bTable[operator] = {}
        self.commutesTable[operator] = commutative
        def registrar(fn):
            self.bTable[operator][(lType, rType)] = fn
            return fn
        return registrar
    
    def apply(self, operator, *args, key=None):
        if len(args) == 1:
            return self.applyUnary(operator, args[0])
        elif len(args) == 2:
            return self.applyBinary(operator, args[0], args[1], key)
        else:
            raise ValueError("????")
    
    def applyUnary(self, operator, u):
        table = self.uTable.get(operator, {})
        fn = table.get(type(u))
        if fn is None:
            return self.defaultTable.get(operator, lambda x:x)(u)
        return fn(u)
    # merge above logic

    def defineDefault(self, operator):
        def registrar(fn):
            self.defaultTable[operator] = fn
            return fn
        return registrar
    
    def applyBinary(self, operator, l,r, key):        
        table = self.bTable.get(operator,{})
        fn = table.get(key)
        if fn is None and self.commutesTable.get(operator, False):
            key = (type(r),type(l))
            fn = table.get(key)
            if fn is not None:
                return fn(r,l)
        
        if fn is None:
            return self.defaultTable.get(operator,lambda x,y: (x,y))(l,r)
        
        return fn(l,r)
    
    

CRbigint = Algebra()
CRfloat = Algebra()
CRalgebra = Algebra()