from ..core import *
from .crconfig import CRconfig
import sympy, hashlib, dataclasses

def construct_tape(env: dict[CR, CRconfig], root: CR ):
    tape = []
    # every node has potentially some children
    for cr in root.postorder():
        env[cr].tape_start = len(tape)
        if not isinstance(cr, (CRnum, CREconnector) ):
            for child in cr: tape.append(child.valueof())
    return tape

def vectorize_tape(tape: list[sympy.Expr], vector_0: sympy.Symbol, vector_h: sympy.Symbol, width: int):
    # after a tape has been made, we can choose to optionally vectorize it
    vectorized = []
    for slot in tape:
        new_slot = []
        for i in range(width):
            new_slot.append(slot.subs([(vector_0, vector_0+i),(vector_h, vector_h*width)]))
        vectorized.append(new_slot)
    return vectorized

def extract_symbols(root: CR) -> list[sympy.Symbol]:
    symbols = {}
    for cr in root.postorder():
        if isinstance(cr, CRnum):
            symbols |= cr.valueof().free_symbols
    return symbols

def partition_orders(env: dict[CR, CRconfig], root: CR):
    symbols = extract_symbols(root)
    sorted_symbols = sorted(symbols, key = str)
    ordering = {}
    traces_byorder = [[] for i in range(len(symbols))]
    for i in range(len(sorted_symbols)):
        symbol = sorted_symbols[i]
        symbol_name = symbol.name
        ordering[symbol_name] = i
    for cr in root.postorder():
        if not isinstance(cr, CRnum):
            traces_byorder[ordering[cr.variable.name]].append(cr)
    return traces_byorder

def assign_suffixhashes(env: dict[CR, CRconfig], root: CR):
    for cr in root.postorder():
        pass

def intern(env: dict[CR, CRconfig], table: dict[bytes, CR], root: CR):
    if isinstance(root, CRnum): return root
    if not env[root].suffix_hashes:
        env[root].suffix_hashes = None

def suffix_hash_default(env: dict[CR, CRconfig], cr: CR):
    if env[cr].suffix_hashes: return
    prev = f"{type(cr)}({cr.variable})".encode()
    suffix_hashes = [None for i in range(len(cr))]
    for i in range(len(cr)):
        h = hashlib.blake2b()
        h.update(prev)
        h.update(env[cr[-i-1]].suffix_hashes[0])
        suffix_hashes[-i-1] = h.digest()
        prev = suffix_hashes[-i-1]
    env[cr].suffix_hashes = suffix_hashes

def suffix_hash_crnum(env: dict[CR, CRconfig], cr: CRnum):
    if env[cr].suffix_hashes: return
    h = hashlib.blake2b()
    s = f"{type(cr)}({sympy.srepr(cr.value)})".encode()
    h.update(s)
    env[cr].suffix_hashes = [h.digest()]

def suffix_hash_crtrig(env: dict[CR, CRconfig], cr: CRtrig):
    if env[cr].suffix_hashes: return
    
    prev = f"CRtrig({cr.variable})".encode()
    suffix_hashes = [None for i in range(len(cr)//2)]
    for i in range(len(cr)//2):
        h = hashlib.blake2b()
        h.update(prev)
        h.update(env[cr[-i-1]].suffix_hashes[0])
        h.update(env[cr[len(cr)//2-i-1]].suffix_hashes[0])
        h.update(b"|")
        suffix_hashes[len(cr)//2-i-1] = h.digest()
        prev = suffix_hashes[len(cr)//2-i-1]
    env[cr].suffix_hashes = suffix_hashes

def intern_full(env: dict[CR, CRconfig], cr: CR, table: dict[bytes, CR]):
    if isinstance(cr, CRnum): 
        suffix_hash_crnum(env, cr)
        return cr
    elif isinstance(cr, CRtrig): suffix_hash_crtrig(env, cr)
    else: suffix_hash_default(env, cr)

    suffixes = env[cr].suffix_hashes
    cr_hash = suffixes[0]

    if cr_hash in table:
        original_cr = table[cr_hash]
        res = CREconnector(original_cr)
        res.parent_type = type(cr)
        return res
    
    else:
        if isinstance(cr, CRtrig):
            return intern_crtrig(suffixes, cr, table)
        else:
            return intern_default(suffixes, cr, table)


def intern_crtrig(suffixes: list[bytes], cr: CRtrig, table: dict[bytes, CR]):
    hl = len(cr)//2
    for i in range(1, hl-1):
        if suffixes[i] in table:
            original_cr = table[suffixes[i]]
            operands = [cr[j].copy() for j in range(i)] + [CREconnector(original_cr, i)] + [cr[j+hl].copy() for j in range(i)] + [CREconnector(original_cr, i+hl)]
            return type(cr)(operands,cr.variable)
        else:
            table[suffixes[i]] = cr
    return cr
        
def intern_default(suffixes: list[bytes], cr: CR, table: dict[bytes, CR]):
    for i in range(1, len(cr)-1):
        if suffixes[i] in table:
            original_cr = table[suffixes[i]]
            operands = [cr[j].copy() for j in range(i)]
            operands.append(CREconnector(original_cr, i))
            return type(cr)(operands, cr.variable)
        else:
            table[suffixes[i]] = cr
    return cr


