from ...core import *
import sympy
import hashlib
# should this just be a file that generates a 
# execute schedule that we hand later to codegen?
# honestly it can be a part of codegen itself

# the tape will be the same if its vectorized or not, we can just store
# all the information we need about it in the vectorized form:
# i.e., x0 := x0 + t; xh := W * xh
# as a result we need to generate tape first and seed last

class CREntry:
    def __init__(self, cr):
        self.cr = cr
        self.suffix_hashes = None
        self.start = None


def construct_tape(cr: CR ):
    tape = []
    # every node has potentially some children
    for cr_node in cr.postorder():
        if not isinstance(cr_node, (CRnum, CREconnector) ):
            for child in cr_node: tape.append(child.valueof())
    return tape

def vectorize_tape(tape: list[sympy.Expr], vector_0: sympy.Symbol, vector_h: sympy.Symbol, width: int):
    vectorized = []
    for slot in tape:
        new_slot = []
        for i in range(width):
            new_slot.append(slot.subs([(vector_0, vector_0+i),(vector_h, vector_h*width)]))
        vectorized.append(new_slot)
    return vectorized

# TODO: assert that we are suffix hashing in postorder
def generate_suffix_hash(env: dict, cr: CR):
    if env[cr].suffix_hashes is not None:
        return env[cr].suffix_hashes
        
    if isinstance(cr, CRnum):
        h = hashlib.blake2b()
        h.update(b"CRnum")
        h.update(sympy.srepr(cr.value).encode())
        result = [h.digest()]

    elif isinstance(cr, CREconnector):
        result = env[cr.operands[0]].suffix_hashes[cr.index]
    
    elif isinstance(cr, (CRsum, CRprod)):
        prev = f"{type(cr)}({cr.variable})".encode()
        result = [None for i in range(len(cr))]
        for i in range(len(cr)):
            h = hashlib.blake2b()
            h.update(prev)
            #h.update(cr[-i-1].crhash())
            h.update(env[cr[-i-1]].suffix_hash)
            h.update(b"|")
            result[-i-1] = h.digest()
            prev = result[-i-1]

def construct_cr_env(cr: CR ):
    cr_env = {}
    for cr_node in cr.postorder():
        cr_env[cr_node] = CREntry(cr)
    return cr_env



def construct_cr_env(cr: CR):
    pass

def construct_cr_trace(cr: CR):
    pass


