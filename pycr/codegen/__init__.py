from .codegen import *
from .dsl import *



def generate_code(crterm, symbol_table, rs = "r"):
    block = Block()
    print(type(block))
    generate_initialize(crterm,block,symbol_table, rs=rs)
    generate_dimension(crterm, block, symbol_table,rs=rs )
    
    
    block.build()
    tree = mod(fn("generated", [], block.stmts))
    ast.fix_missing_locations(tree)
    return tree

    


