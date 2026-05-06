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

    def __init__(self,cr, symbol_table = None):
        self.cr = cr

        # hold original cr, but we can perform CSE or transformations on a temporary copy
        self.cse_cr = cr
        # no need for truncation
        # purpose of symbol table here is to seed the CR when we need it.
        # we construct a temporary CR and seed it with values
        self.symbol_table = symbol_table

        # after seeding, we hold the partitions of the CR.
        # we separate the entire tree into different CRs where each CR
        # pertains to a different order. 
        self.orders = []
        # the register tape of each of the leaf nodes in the CR tree.
        self.tape = []

    def prepare(self):
        # partitions the orders, produces the tape, evaluates floats
        # everything before generating the code. 
        pass

    def partition_orders(self):
        # root will have highest order
        n_orders = self.cr.order
        self.orders = [[] for i in range(n_orders)]
        for member in self.cr.postorder():
            member_order = member.order
            self.orders[member_order].append()

    def construct_tape(self):
        pass

    def evaluate_tape(self):
        pass
    
    # todo:
    # move these


def cse(table, cr: CR):
    if isinstance(cr, CRnum):
        return cr
    operands = [cse(operand) for operand in cr]
    copy = type(cr)(operands, cr.order)
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
    for i in range(1,  len(cr)-1):
        if suffixes[i] in table:
            original_cr = table[suffixes[i]]
            if isinstance(cr, CRtrig):
                hl = len(cr) //2
                operands = [cr[j].copy() for j in range(i)] + [CREconnector(original_cr, i)] + [cr[j+hl] for j in range(i)] + [ CREconnector(original_cr, i+hl)]
            else:
                operands = [cr[j].copy() for j in range(i)]
                operands.append(CREconnector(original_cr, i))
            return type(cr)(operands, cr.order)
        else:
            table[suffixes[i]] = cr
    return cr

