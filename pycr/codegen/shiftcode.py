from .dsl import *
from core import *


def generate_codeblock(term, register_symbol='r'):
    if isinstance(term.cr, CRnum):
        pass

    elif isinstance(term.cr, CRsum):
        block = []
        for i in range(len(term.cr)-1):
            block.append(   
                AugAssign(
                    ast.Add(),
                    IndexS(S(f"{register_symbol}_{term.start + i}"), C(0)),
                    IndexL(S(f"{register_symbol}_{term.start + i + 1}"), C(0)),
                )
            )
        return block
    
    elif isinstance(term.cr, CRprod): 
        block = []
        for i in range(len(term.cr)):
            block.append(
                AugAssign(
                    ast.Mult(),
                    IndexS(S(f"{register_symbol}_{term.start}"), C(0)),
                    IndexL(S(f"{register_symbol}_{term.start + i}"), C(0)),
                )
            )
        return block
    
    elif isinstance(term.cr, CRtrig):
        pass

    # serve no other purpose than to lift child emitters
    elif isinstance(term.cr, CRE):
        pass
        
def generate_updateblock(term, register_symbol='r'):
    block = []
    for source, parent, index in term.update:
        block.append(
            Assign(
                IndexS(S(f"{register_symbol}_{parent.start + index}"), C(0) ),
                IndexL(S(f"{register_symbol}_{source}"), C(0) )
        ))
    return block

