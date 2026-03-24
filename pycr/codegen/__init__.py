from .codegen import *
from .dsl import *



def generate_code(crterm, symbol_table, rs = "r"):
    block = Block()
    print(type(block))

    
    block.build()
    tree = mod(fn("generated", [], block.stmts))
    ast.fix_missing_locations(tree)
    return tree

    
def generate_code(ir):
    block = gen_nested(ir)
    B = [f"B_{i}" for i in range(len(ir.st))]
    tree = mod(fn("generated", ['A','R'] + B, block.stmts))
    ast.fix_missing_locations(tree)
    return tree


