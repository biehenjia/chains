import sys, hashlib
from sympy import srepr
from core import *

PROTOCOL = hashlib.blake2b

class CRterm:

    def __init__(self, cr, parent_update):
        self.cr = cr
        self.digests = None
        self.node_id = None

        self.start = None

        # (source_index, parent, update_index) pairs
        self.parents = [parent_update]
        self.update_indices = []
        # terminus node
        if isinstance(cr, CRnum):
            pass
        # has children type node
        else:
            self.terms = [CRterm(t, (self, i)) for i, t in enumerate(cr)]
    
    # produces tape representation of the required expression from CR form
    def produce_tape(self):
        tape = []
        for t in self.postorder():
            if isinstance(t.cr, CRnum):
                continue
            t.start = len(tape)
            for i in range(len(t.cr)):
                tape.append(t.cr[i].valueof())
        return tape
    
    def postorder(self):
        if isinstance(self.cr, CRnum):
            return
        for t in self.terms:
            yield from t.postorder()
        yield self

    def crdigest(self):
        
        # do not cache CRnum digests... probably not worth it
        if isinstance(self.cr, CRnum):
            h = PROTOCOL(digest_size=16)
            h.update(b"CRnum|")
            h.update(srepr(self.cr.value).encode("utf-8"))
            self.digests = [h.digest()]
            return self.digests[0]
        
        if self.digests is not None:
            return self.digests[0]
        
        h = PROTOCOL(digest_size=16)
        h.update(type(self.cr).__name__.encode())
        # compute suffix hash
        self.digests = [None] * (len(self.cr))
        for i in range(len(self.cr)):
            h.update(self.terms[-i-1].crdigest())
            self.digests[-i-1] = h.digest()
        return self.digests[0]
    
    def cse(self):
        id_map = {}
        memo = {}

        # label nodes:
        for node in self.postorder():
            if isinstance(node.cr, CRnum):
                continue
            node.crdigest()
            for i in range(len(node.digests)):
                suffix = node.digests[i]
                if suffix not in id_map:
                    node_id = len(id_map)
                    id_map[node_id] = (node, i)
                    memo[suffix] = node_id
                else:
                    original,p = id_map[memo[suffix]]
    
    def codegen(self):
        pass

   