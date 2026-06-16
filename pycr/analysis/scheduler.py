from ..core import CR, CRnum, CREconnector
from ..crconfig import CRconfig
import sympy

def construct_tape(env: dict[CR, CRconfig], root: CR ) -> list[sympy.Expr]:
    """
    Constructs a list of SymPy expression objects in the argument order for a CRfunction
    
    :type env: dict[CR, CRconfig]
    :type root: CR
    :rtype: list[Expr]
    """
    tape = []
    # every node has potentially some children
    seen = set()
    for cr in root.postorder():
        if isinstance(cr, CREconnector):
            env[cr].tape_start = len(tape)
            tape.append(cr.valueof())
        elif not isinstance(cr, CRnum ):
            if cr in seen:
                continue
            seen.add(cr)
            env[cr].tape_start = len(tape)
            
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
    symbols = set()
    for cr in root.postorder():
        if not isinstance(cr, CRnum):
            symbols |= {cr.variable}
    return sorted(symbols,key=str)

def partition_orders(env: dict[CR, CRconfig], root: CR):
    symbols = extract_symbols(root)
    ordering = {}
    traces_byorder = [[] for i in range(len(symbols))]
    
    for i in range(len(symbols)):
        symbol = symbols[i]
        symbol_name = symbol.name
        ordering[symbol_name] = i
    
    seen = set()
    for cr in root.postorder():
        if not isinstance(cr, CRnum):
            if cr in seen:
                continue

            traces_byorder[ordering[cr.variable.name]].append(cr)
            seen.add(cr)

    return traces_byorder



