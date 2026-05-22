from ..core import *
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
        self.cse_cr = cr
        self.orders = []
        self.tape = []

    def prepare(self, vectorized = False):
        """
        prepares the CRterm for vectorization. 
        
        :param self: Description
        :param vectorized: Description
        """
        total_length = self.align_starts()
        self.construct_tape(total_length)
        self.partition_orders()
        if vectorized:
            self.vectorize_tape()

    def partition_orders(self):
        # root will have highest order
        n_orders = self.cr.order
        self.orders = [[] for i in range(n_orders+1)]
        for member in self.cr.postorder():
            if isinstance(member, CRnum):
                continue
            member_order = member.order
            self.orders[member_order].append(member)

    def construct_tape(self, total_length):
        p = list(self.cr.postorder())
        self.tape = [p[i].valueof() for i in range(total_length)]

    def evaluate_tape(self):
        pass

    def align_starts(self):
        postorder = self.cr.postorder()
        i = 0
        for cr in postorder:
            if isinstance(cr, CRnum):
                continue
            cr.start = i
            i += len(cr)
        return i
    
    def vectorize_tape(self):
        newtape = [None for i in range(len(self.tape))]

        for i in range(len(self.tape)):
            piece = [None for i in range(4)]
            for j in range(4):
                piece[j] = self.tape[i].subs('t',j)
            newtape[i] = piece
        
        self.tape = newtape

                
    # todo:
    # move these


def cse(table, cr: CR):
    if isinstance(cr, CRnum):
        return cr
    operands = [cse(table, operand) for operand in cr]
    copy = type(cr)(operands, cr.variable)
    return intern(table, copy)

def intern(table, cr: CR):
    if isinstance(cr, CRnum):
        return cr
    crhash = cr.crhash()
    suffixes = cr._suffixhash()
    if crhash in table:
        original_cr = table[crhash]
        return CREconnector(original_cr)
    else:
        table[crhash] = cr
    if isinstance(cr, CRtrig):
        hl = len(cr)//2
        for i in range(1, hl- 1):
            if suffixes[i] in table:
                original_cr = table[suffixes[i]]
                operands = [cr[j].copy() for j in range(i)]
                operands += [CREconnector(original_cr,i )]
                operands +=[cr[j+hl] for j in range(i)]
                operands += [CREconnector(original_cr,i+hl)]
                return CRtrig(operands, cr.variable)
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