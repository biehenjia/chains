
'''
PURPOSE OF CRTERM:

Given an expression, and that we have already constructed the corresponding chain of recurrence, we would like:
    1. To remove commmon subchains from the chain of recurrence
    2. To construct a minimal "tape" and set of rules


'''

'''
Computation graph of CRterm

    1. convert CR into CRterm

    2. CSE:
        1. For each term T in the CRterm postorder:
            1. compute the suffix hash for every possible suffix
                1. If the suffix exists already, then we set the suffix at that position to be a child of T at that position

                in other words, in the generated code, before we compute T, we want to read all of the relevant updates, and this means that
                we read arrays at the relevant indices into the proper locations. ((source, index1), index2), where index1 is in the source.
                This can be read by grabbing the start index of source and adding index1. 

                2. Set the start of the maximum suffix to have a descendent of the CR, and truncate the CR of T.

    3. Propogate dependencies:
        1. For each term T in the CRterm postorder:
            Set its dependencies to be the union of those of its children

    4. Code generation:
        1. For every order, i.e., the possible dimensions of the shift variables, gather the associated CRterms. If the order matches, then we 
        add a code block for the specific shift type. If the order does not match, we need to propogate the changes of the descendants upwards. 

        2.  
'''
from ..core import *
from ..codegen import *

import hashlib
from sympy import srepr

PROTOCOL = hashlib.blake2b
class CRterm:

    def __init__(self, cr):
        self.cr = cr
        self.digests = []
        self.trunc = len(cr)
        self.dependencies = {cr.order,}
        self.operands = []
        self.updates = []
        if not isinstance(self.cr, CRnum):
            self.trunc = len(self.cr)
            #print(type(self.cr),len(self .cr))
            # base update spot
            
            for i in range(len(self.cr)):
                self.operands.append(CRterm(self.cr[i]))
                
                # DONT DO UPDATES UNTIL AFTER CSE. THEN, WE CAN DO LAST INDEX AS THE WRITE REGISTER.


    def postorder(self):
        if not isinstance(self.cr, CRnum):
            for t in self.operands:
                yield from t.postorder()
            yield self

    def crdigest(self):
        if self.digests:
            return self.digests[0]
        

        if isinstance(self.cr, CRnum):
            h = PROTOCOL(digest_size=16)
            h.update(b"CRnum")
            h.update(srepr(self.cr.value).encode("utf-8"))
            self.digests = [h.digest()]
            
        elif isinstance(self.cr, CRtrig):
            h = PROTOCOL(digest_size = 16)
            h.update(b"CRtrig")
            self.digests = [None] * (len(self.cr)//2)
            for i in range(len(self.cr)//2):
                h.update(self.operands[-i-1].crdigest())
                h.update(self.operands[-i-1 - len(self.cr)//2].crdigest())
                self.digests[-i-1] = h.digest()
        
        else:
            h = PROTOCOL(digest_size=16)
            h.update(type(self.cr).__name__.encode())
            # compute suffix hash
            self.digests = [None] * (len(self.cr))
            for i in range(len(self.cr)):
                h.update(self.operands[-i-1].crdigest())
                self.digests[-i-1] = h.digest()
        
        return self.digests[0]

    def propogate_dependencies(self):
        for term in self.postorder():
            if isinstance(term.cr, CRnum):
                continue
            for child in term.operands:
                term.dependencies |= child.dependencies
    
    def cr_seed(self, symbol_table):
        env = {}
        for (s_0, s_h) in symbol_table.items:
            pass

        for crt in self.postorder():
            crt.cr

    def cse(self):
        memo = {}
        id_map = {}
        s = list(self.postorder())
        s.sort(key = lambda x: -len(x.cr))

        for c in s:

            if isinstance(c.cr, CRnum):
                continue
            c.crdigest()
            for i in range(1,len(c.digests)):
                digest = c.digests[i]
                if digest in memo:
                    source, index = memo[digest]
                    c.updates.append((i, source, index))
                    c.trunc = min(c.trunc, i)
                else:
                    memo[digest] = (c, i)

    def partition_order(self, symbol_table):
        orders = [[] for i in range(len(symbol_table))]
        for c in self.postorder():
            for d in c.dependencies:
                if d >= 0:
                    orders[d].append(c)
        return orders
    
    # this will be the preparation code generation place
    # we will try and produce the tape, and also update the things that we need such as update indices 
    def prepare(self, symbol_table, cse = True):
        if cse:
            self.cse() # optional
        self.propogate_dependencies()
        self.partition_order(symbol_table)
        tape = self.produce_tape()
        return tape
    
    # produces and also assigns the starts and mids of the crterm
    def produce_tape(self):
        s = self.postorder()
        tape = []
        for c in s:
            c.start = len(tape)
            c.mid = len(tape) + len(c.cr)//2
            for i in range(c.trunc):

                tape.append(c.cr.operands[i].valueof())
                if not isinstance(c.cr.operands[i], CRnum):
                    self.updates.append((len(tape)-1, c.operands[i], c.operands[i].trunc ))
            c.update_index = len(tape)
            tape.append(c.cr.valueof())
        return tape
    
    def codegen(self, symbol_table, out_name, tape):
        orders = self.partition_order(symbol_table)
        
        # for order in orders:
        #     for term in order:
        #         print(type(term.cr), term.trunc)
        blocks = []
        for order in orders:
            blocks.append([])
            for instruction in order:
                temp_block = [gen_fetch(instruction), gen_shift(instruction), gen_update(instruction)]
                blocks[-1].append(temp_block)
        # returns AST object that compiles the generated code
        return gen_nested(blocks, symbol_table,out_name=out_name, n_registers=len(tape))