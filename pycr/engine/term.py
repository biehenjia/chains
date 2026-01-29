import sys, hashlib, struct

PROTOCOL = hashlib.blake2b
class Term:
    # wrap CR node; tape is shared.
    def __init__(self, cr, tape):
        self.order = cr.order
        self.cr = cr
        self.terms = [Term(t, tape) for t in cr]

        self.digests = [None] * len(self.terms)
        self.tape = tape
    
    def __getitem__(self, key):
        return self.terms[key]
    
    def __setitem__(self, key, value):
        self.terms[key] = value

    def __len__(self):
        return len(self.terms)
    
    def crdigest(self):
        pass
        


    

    
