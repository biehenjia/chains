from ..core import *

# purpose
'''
After constructing the CR tree, they each have CRterm wrappers that hold 
metadata about the CR before we convert it it into the relevant code generation

Essentially their only purpose is to codegen

''' 
# use duck typing
# 
class CRconnector:
    
    # the index will be found at the same distance from the tail
    def __init__(self, source, target, index=0):
        pass

    def shift(self):
        pass



# wraps the root of a CR node that we will be working with
"""
RESPONSABILITIES:

- owns root of CR node
- holds partition information, i.e., ordering
- holds bounds information (? can be stateless)


"""
class CRterm:
    def __init__(self,cr, symbol_table = None):
        self.cr = cr
        # no need for truncation
        self.symbol_table = symbol_table


# TODO: conver to class function in CRterm. 
# pattern: 
def intern(table, cr: CR):
    if isinstance(cr, CRnum):
        return cr
    
    crhash = cr.crhash()
    suffixes = cr._suffixhash()
    if crhash in table:
        original_cr = table[crhash] # original crhash location
        return CRconnector(original_cr, cr)
    else:
        table[crhash] = cr
    
    for i in range(1, len(cr)-1):
        if suffixes[i] in table:
            # cant use negative indexing:must be objectively at len(cr)-i-1
            # i think... 
            return CRconnector(table[suffixes[i]], cr, len(cr)-i-1)
        
    # no match found
    return cr

# accepts root of the CR tree and partitions all subtree nodes into their
# respective orders
def partition_ordering(root):
    pass

