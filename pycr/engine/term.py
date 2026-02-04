from ..core import *
import hashlib
from sympy import srepr


PROTOCOL = hashlib.blake2b


class CRterm:

    def __init__(self, cr, parent):
        self.cr = cr 

        if not isinstance(cr, CRnum):
            # hashing is based on subarena
            self.subarena = []
            self.terms = []
            self.digests = []
            self.dependencies = {cr.order,}
            for i,o in enumerate(cr):
                self.subarena.append(o.valueof())
                self.terms.append( CRterm(o, (self,i)) )
    
    def cse(self):
        if not isinstance(self.cr, CRnum):
            pass

    def postorder(self):
        if isinstance(self.cr, CRnum):
            return 
        for t in self.terms:
            yield from t.postorder()
        yield self 
            
    def crdigest(self):
        if self.digests is not None:
            return self.digests[0]
        
        if isinstance(self.cr, CRnum):
            h = PROTOCOL(digest_size=16)
            h.update(b"CRnum|")
            h.update(srepr(self.cr.value).encode("utf-8"))
            self.digests = [h.digest()]
            return self.digests[0]
        
        elif isinstance(self.cr, CRtrig):
            pass
        else:
            h = PROTOCOL(digest_size=16)
            h.update(type(self.cr).__name__.encode())
            # compute suffix hash
            self.digests = [None] * (len(self.cr))
            for i in range(len(self.cr)):
                h.update(self.terms[-i-1].crdigest())
                self.digests[-i-1] = h.digest()
        return self.digests[0]

    def propogate_dependencies(self):
        for term in self.postorder():
            if isinstance(term.cr, CRnum):
                continue
            for child in term.terms:
                term.dependencies |= child.dependencies
    
    # returns all of the terms who's CR's need to be shifted when we
    # shift by that order.
    def partition_byorder(self, symbol_table):
        buckets = [[] for _ in range(len(symbol_table))]
        for term in self.postorder():
            if isinstance(term.cr, CRnum):
                continue
            for dep in term.dependencies:
                buckets[dep].append(term)
        return buckets
    
    