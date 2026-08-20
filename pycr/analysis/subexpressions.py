from ..crconfig import CRconfig
from ..core import CR, CRnum, CRtrig, CREconnector
import hashlib, sympy

def prepare_cse(env: dict[CR, CRconfig], root: CR):
    """
    Attaches the suffix hashes to their keyed entries within the CR environment in postorder.

    :param env: the CRenvironment
    :type env: dict[CR, CRconfig]
    :param root: the root of the CR
    :type root: CR
    """
    for cr in root.postorder():
        if isinstance(cr, CRnum): _suffix_hash_crnum(env, cr )
        elif isinstance(cr, CRtrig): _suffix_hash_crtrig(env, cr)
        else: _suffix_hash_default(env, cr)

def cse(env: dict[CR, CRconfig], table: dict[bytes, CR], cr:CR):
    """
    Performs common subexpression elimination of CRs

    :param env: the CRenvironment
    :type env: dict[CR, CRconfig]
    :param table: the cons table
    :type table: dict[bytes, CR]
    :param cr: the root of the CR
    :type cr: CR
    """
    if isinstance(cr, CRnum): return cr
    if isinstance(cr, CREconnector): return cr
    cr.operands = [cse(env, table, operand) for operand in cr]
    return intern_full(env, cr, table)

def _child_hash(env: dict[CR, CRconfig], child: CR) -> bytes:
    """
    A child's contribution to its parent's hash. CRtrig's own suffix_hashes
    are deliberately type-erased (a CRsin and CRcos sharing the same operands
    hash equal, so they can share storage via a CREconnector, which records
    the concrete type separately for correct access). That erasure is only
    safe within CRtrig-to-CRtrig matching — a parent (CRtrig or otherwise)
    folding a child's hash into its OWN identity needs to know the child's
    concrete type too, since e.g. cos(a)*b and sin(a)*b are different values
    even when a's underlying quadruple is shared.
    """
    return f"{type(child)}".encode() + env[child].suffix_hashes[0]

def _suffix_hash_default(env: dict[CR, CRconfig], cr: CR):
    """
    Performs the default suffix hash for CRsum, CRprod, and CREs

    :param env: the CRenvironment
    :type env: dict[CR, CRconfig]
    :param cr: the root of the CR
    :type cr: CR
    """
    if env[cr].suffix_hashes: return
    prev = f"{type(cr)}({cr.variable})".encode()
    suffix_hashes = [None for i in range(len(cr))]
    for i in range(len(cr)):
        h = hashlib.blake2b()
        h.update(prev)
        h.update(_child_hash(env, cr[-i-1]))
        suffix_hashes[-i-1] = h.digest()
        prev = suffix_hashes[-i-1]
    env[cr].suffix_hashes = suffix_hashes

def _suffix_hash_crnum(env: dict[CR, CRconfig], cr: CRnum):
    """
    Performs the suffix hash for CRnum leaf nodes.
    
    :param env: the CRenvironment
    :type env: dict[CR, CRconfig]
    :param cr: the root of the CR
    :type cr: CRnum
    """
    if env[cr].suffix_hashes: return
    h = hashlib.blake2b()
    s = f"{type(cr)}({sympy.srepr(cr.value)})".encode()
    h.update(s)
    env[cr].suffix_hashes = [h.digest()]

def _suffix_hash_crtrig(env: dict[CR, CRconfig], cr: CRtrig):
    """
    Performs the suffix hash for CRtrig nodes.
    
    :param env: the CRenvironment
    :type env: dict[CR, CRconfig]
    :param cr: the root of the CR
    :type cr: CRtrig
    """
    if env[cr].suffix_hashes: return
    prev = f"CRtrig({cr.variable})".encode()
    suffix_hashes = [None for i in range(len(cr)//2)]
    for i in range(len(cr)//2):
        h = hashlib.blake2b()
        h.update(prev)
        h.update(_child_hash(env, cr[-i-1]))
        h.update(_child_hash(env, cr[len(cr)//2-i-1]))
        h.update(b"|")
        suffix_hashes[len(cr)//2-i-1] = h.digest()
        prev = suffix_hashes[len(cr)//2-i-1]
    env[cr].suffix_hashes = suffix_hashes

def intern_full(env: dict[CR, CRconfig], cr: CR, table: dict[bytes, CR]):
    """
    Dynamic dispatch function for interning CR nodes by type
    
    :param env: the CRenvironment
    :type env: dict[CR, CRconfig]
    :param cr: root of the CR
    :type cr: CR
    :param table: CR CSE intern table
    :type table: dict[bytes, CR]
    """
    if isinstance(cr, CRnum): 
        _suffix_hash_crnum(env, cr)
        return cr
    # elif isinstance(cr, CRtrig): _suffix_hash_crtrig(env, cr)
    # else: _suffix_hash_default(env, cr)

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
    """
    Intern function for CRtrig
    
    :param suffixes: Description
    :type suffixes: list[bytes]
    :param cr: Description
    :type cr: CRtrig
    :param table: Description
    :type table: dict[bytes, CR]
    """
    hl = len(cr)//2
    for i in range(1, hl-1):
        if suffixes[i] in table:
            original_cr = table[suffixes[i]]
            operands = [cr[j].copy() for j in range(i)] + [CREconnector(original_cr, i)] + [cr[j+hl].copy() for j in range(i)] + [CREconnector(original_cr, i+hl)]
            return type(cr)(operands,cr.variable)
        else:
            table[suffixes[i]] = cr
    table[suffixes[0]] = cr
    return cr
        
def _intern_default(suffixes: list[bytes], cr: CR, table: dict[bytes, CR]):
    """
    Intern function for CRprod and CRsum types.
    
    :param suffixes: Description
    :type suffixes: list[bytes]
    :param cr: Description
    :type cr: CR
    :param table: Description
    :type table: dict[bytes, CR]
    """
    for i in range(1, len(cr)-1):
        if suffixes[i] in table:
            original_cr = table[suffixes[i]]
            # shared-suffix lengths must match: len(cr)-i == len(original_cr)-src_j
            src_j = len(original_cr) - (len(cr) - i)
            operands = [cr[k].copy() for k in range(i)]
            operands.append(CREconnector(original_cr, src_j))
            return type(cr)(operands, cr.variable)
        else:
            table[suffixes[i]] = cr
    table[suffixes[0]] = cr
    return cr