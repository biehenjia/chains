from .crconfig import CRconfig
from ..core import *
import hashlib, sympy

def cse(table: dict[bytes, CR], cr:CR):
    if isinstance(cr, CRnum): return cr
    operands = [cse(table, operand) for operand in cr]
    copy = type(cr)(operands, cr.variable)

def _suffix_hash_default(env: dict[CR, CRconfig], cr: CR):
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

def _suffix_hash_crnum(env: dict[CR, CRconfig], cr: CRnum):
    if env[cr].suffix_hashes: return
    h = hashlib.blake2b()
    s = f"{type(cr)}({sympy.srepr(cr.value)})".encode()
    h.update(s)
    env[cr].suffix_hashes = [h.digest()]

def _suffix_hash_crtrig(env: dict[CR, CRconfig], cr: CRtrig):
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
        _suffix_hash_crnum(env, cr)
        return cr
    elif isinstance(cr, CRtrig): _suffix_hash_crtrig(env, cr)
    else: _suffix_hash_default(env, cr)

    suffixes = env[cr].suffix_hashes
    cr_hash = suffixes[0]

    if cr_hash in table:
        original_cr = table[cr_hash]
        res = CREconnector(original_cr)
        res.original = cr
        return res
    
    else:
        if isinstance(cr, CRtrig):
            return _intern_crtrig(suffixes, cr, table)
        else:
            return _intern_default(suffixes, cr, table)

def _intern_crtrig(suffixes: list[bytes], cr: CRtrig, table: dict[bytes, CR]):
    hl = len(cr)//2
    for i in range(1, hl-1):
        if suffixes[i] in table:
            original_cr = table[suffixes[i]]
            operands = [cr[j].copy() for j in range(i)] + [CREconnector(original_cr, i)] + [cr[j+hl].copy() for j in range(i)] + [CREconnector(original_cr, i+hl)]
            return type(cr)(operands,cr.variable)
        else:
            table[suffixes[i]] = cr
    return cr
        
def _intern_default(suffixes: list[bytes], cr: CR, table: dict[bytes, CR]):
    for i in range(1, len(cr)-1):
        if suffixes[i] in table:
            original_cr = table[suffixes[i]]
            operands = [cr[j].copy() for j in range(i)]
            operands.append(CREconnector(original_cr, i))
            return type(cr)(operands, cr.variable)
        else:
            table[suffixes[i]] = cr
    return cr