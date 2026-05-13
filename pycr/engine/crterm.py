from ..core import *

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

    def __init__(self,cr):
        self.cr = cr

        # hold original cr, but we can perform CSE or transformations on a temporary copy
        self.cse_cr = cr
        # no need for truncation
        # purpose of symbol table here is to seed the CR when we need it.
        # we construct a temporary CR and seed it with values

        # after seeding, we hold the partitions of the CR.
        # we separate the entire tree into different CRs where each CR
        # pertains to a different order. 
        self.orders = []
        # the register tape of each of the leaf nodes in the CR tree.
        self.tape = []

    def prepare(self):
        total_length = self.align_starts()
        self.construct_tape(total_length)
        self.partition_orders()
        pass

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
    
    # todo:
    # move these


def cse(table, cr: CR):
    if isinstance(cr, CRnum):
        return cr
    operands = [cse(table, operand) for operand in cr]
    copy = type(cr)(operands, cr.order)
    return intern(table, copy)

def intern(table, cr: CR):
    if isinstance(cr, CRnum):
        return cr
    crhash = cr.crhash()
    suffixes = cr._suffixhash()
    if crhash in table:
        original_cr = table[crhash]
        # if type mismatch in the trig case then we can still connect
        # construct new CR in the place of it with proper values 
        
        
        # current issue: CRE connector will match all trig types
        # work is reused, but we want to maintain the grab index
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
                return CRtrig(operands, cr.order)
            else:
                table[suffixes[i]] = cr
                pass
        return cr 
    # CRsum, CRprod case
    else:
        for i in range(1, len(cr)-1):
            if suffixes[i] in table:
                operands = [cr[j].copy() for j in range(i)]
                operands.append(CREconnector(original_cr, i))
                return type(cr)(operands, cr.order)
            else:
                table[suffixes[i]] = cr
    
    return cr