from .dsl import *
from ..core import *

from ast import *

# CHANGE TO ACCEPT JUst AN ARRAY. WE KNOW THE OPERATION.
def generate_shift(term, register_symbol='r'):
    if isinstance(term.cr, CRnum):
        pass

    elif isinstance(term.cr, CRsum):
        block = []
        for i in range(len(term.cr) - 1):
            block.append(
                AugAssign(
                    S(f"{register_symbol}_{term.start+i}"),
                    ast.Add(),
                    L(f"{register_symbol}_{term.start + i + 1}"),
                )
            )
        return block

    
    elif isinstance(term.cr, CRprod): 
        block = []
        for i in range(len(term.cr) - 1):
            block.append(
                AugAssign(
                    S(f"{register_symbol}_{term.start}"),
                    ast.Mult(),
                    L(f"{register_symbol}_{term.start + i + 1}"),
                )
            )
        return block
    
    elif isinstance(term.cr, CRtrig):
        block = []
        n = len(term.cr)
        t = n // 2

        for i in range(t - 1):
            a   = S(f"{register_symbol}_{term.start + i}")
            b   = S(f"{register_symbol}_{term.start + t + i}")
            ap1 = L(f"{register_symbol}_{term.start + i + 1}")
            bp1 = L(f"{register_symbol}_{term.start + t + i + 1}")

            # a = a*bp1 + b*ap1
            block.append(
                Assign(
                    [a],
                    BinOp(
                        BinOp(L(a.id), ast.Mult(), bp1),
                        ast.Add(),
                        BinOp(L(b.id), ast.Mult(), ap1),
                    ),
                )
            )

            # b = b*bp1 - a_old*ap1
            block.append(
                Assign(
                    [b],
                    BinOp(
                        BinOp(L(b.id), ast.Mult(), bp1),
                        ast.Sub(),
                        BinOp(L(a.id), ast.Mult(), ap1),
                    ),
                )
            )

        return block


    # serve no other purpose than to lift child emitters
    elif isinstance(term.cr, CRE):
        pass

def generate_code(bounds, terms_per_order, register_symbol='r'):
    # bounds is a list of dimensions, i.e., number of steps.
    blocks = []
    for i in range(len(bounds)):
        # for loop of size bounds[i]
        body = []
        for term in terms_per_order[i]:
            body.extend(generate_shift(term, register_symbol))
            body.extend(generate_update(term, register_symbol))
        loop = For(S(f"i_{i}"), Call(L('range'), C(bounds[i])), body)
        blocks.append(loop)
    return blocks

    

def generate_update(term, register_symbol="r"):

    return [
        Assign(
            S(f"{register_symbol}_{parent.start + index}"),
            L(f"{register_symbol}_{source}"),
        )
        for source, parent, index in term.update
    ]


