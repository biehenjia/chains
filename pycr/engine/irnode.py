from ..core import *


class IR:

    def __init__(self, cr, st):
        self.cr = cr # cr
        self.st = st # symbol table
        self._cr = cr # original cr, for when we cse, transform, vectorize, etc...

        self.starts = {} # information about the crs that we use
        self.tape = [] # contiguous tape
        self.orders = []

    def postorder(self):
        return self.cr.postorder()
    
    # fix later
    def cse(self):
        pass
    
    def seed(self, st):
        self.st = st
    

    def partition(self):
        orders = [[] for _ in self.st ]
        s = self.cr.postorder()
        for c in s:
            if not isinstance(c, CRnum):
                orders[c.order].append(c)
        # list of cr's
        self.orders = orders


    # no more update index for CRE types
    def prepare(self):
        self.partition()
        tape = []
        for i, order in enumerate(self.orders):
            for c in order:
                # the start of the block representing s: the cr
                self.starts[c] = len(tape)
                if isinstance(c, CRE):
                    tape.append(c.valueof())
                else:
                    for operand in c:
                        tape.append(operand.valueof())
        self.tape = tape
        print(self.cr)


    def vectorize(self):
        order = -1
        
    
    def printape(self):
        print(self.tape)

    
    
            


    



    
    
    


    
    

    