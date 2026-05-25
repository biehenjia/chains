from .core import *
import sympy
# purpose
'''
After constructing the CR tree, they each have CRterm wrappers that hold 
metadata about the CR before we convert it it into the relevant code generation

Essentially their only purpose is to codegen

''' 
# use duck typing
# wraps the root of a CR node that we will be working with
"""
RESPONSABILITIES:

- owns root of CR node
- holds partition information, i.e., ordering
- holds bounds information (? can be stateless)
"""

class CRterm:
    cr: CR
    tape: list[sympy.Expr]

    def __init__(self,cr):
        self.cr = cr
        self.varmap = None
        self.orders = []
        self.tape = []

    def prepare(self, environment, eliminate=False, vectorization = 1, outer_step=None):
        if eliminate:
            self.cr = cse({}, self.cr)
        
        # total_length = self.align_starts()
        self.construct_tape()
        self.sort_variables() 
        self.partition_orders()
        if vectorization> 1 :
            self.vectorize_tape(vectorization, outer_step)
            
        
        self.evaluate_tape(environment, vectorization > 1)
        # for col in self.tape:
        #     if vectorization > 1:
        #         print(" ".join(list(map(str,col))))
        #     else:
        #         print(col)

    def sort_variables(self):
        variables = set()
        for node in self.cr.postorder():
            if isinstance(node, CRnum): continue
            variables.add(node.variable)
        orders = sorted(variables, key = lambda x: x.name)
        self.varmap = {orders[i]:i for i in range(len(orders))}
        
    def partition_orders(self):
        # root will have highest order
        n_orders = len(self.varmap)
        self.orders = [[] for i in range(n_orders)]
        for member in self.cr.postorder():
            if isinstance(member, CRnum):
                continue
            self.orders[self.varmap[member.variable]].append(member)

    def construct_tape(self):
        p = list(self.cr.postorder())
        tape = []
        for cr in p:
            if not isinstance(cr, CRnum):
                cr.start = len(tape)
                for operand in cr:
                    tape.append(operand.valueof())
        self.tape = tape
        
    
    def evaluate_tape(self, environment, vectorized = False):
        if vectorized:
            for i in range(len(self.tape)):
                for j in range(len(self.tape[i])):
                    self.tape[i][j] = (self.tape[i][j].subs(environment))
        else:
            for i in range(len(self.tape)):
                self.tape[i] = (self.tape[i].subs(environment))
        
        

    # def align_starts(self):
    #     postorder = self.cr.postorder()
    #     i = 0
    #     for cr in postorder:
    #         if isinstance(cr, CRnum):
    #             continue
    #         cr.start = i
    #         i += len(cr)
    #     return i
    
    def vectorize_tape(self, vectorization, outer_step):
        newtape = [None for i in range(len(self.tape))]
        for i in range(len(self.tape)):
            piece = [None for i in range(vectorization)]
            for j in range(vectorization):
                piece[j] = self.tape[i].subs('t',j*outer_step)
            newtape[i] = piece
        self.tape = newtape
    


def cse(table, cr: CR):
    if isinstance(cr, CRnum): return cr
    operands = [cse(table, operand) for operand in cr]
    copy = type(cr)(operands, cr.variable)
    return intern(table, copy)

def intern(table, cr: CR):
    if isinstance(cr, CRnum): return cr
    crhash = cr.crhash()
    suffixes = cr._suffixhash()
    if crhash in table:
        original_cr = table[crhash]
        res = CREconnector(original_cr)
        res.parent_type = type(cr)
        return res
    else:
        table[crhash] = cr
    if isinstance(cr, CRtrig):
        hl = len(cr)//2
        for i in range(1, hl- 1):
            if suffixes[i] in table:
                original_cr = table[suffixes[i]]
                operands = [cr[j].copy() for j in range(i)]
                operands += [CREconnector(original_cr,i )]
                operands +=[cr[j+hl].copy() for j in range(i)]
                operands += [CREconnector(original_cr,i+hl)]
                return type(cr)(operands, cr.variable)
            else:
                table[suffixes[i]] = cr
                pass
        return cr 
    else:
        for i in range(1, len(cr)-1):
            if suffixes[i] in table:
                operands = [cr[j].copy() for j in range(i)]
                operands.append(CREconnector(original_cr, i))
                return type(cr)(operands, cr.variable)
            else:
                table[suffixes[i]] = cr
    
    return cr