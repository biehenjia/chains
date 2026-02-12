from .api import *
from .codegen import *
from .core import *
from .engine import * 

def chainify(expr_string):
    expr_symbolic, symbol_table = parse_string(expr_string)
    cr = crmake(expr_symbolic,symbol_table)
    return cr, symbol_table

def chain_ast(expr_string):
    cr, symbol_table = chainify(expr_string)
    crt = CRterm(cr)
    tape = crt.prepare(symbol_table)
    statements = crt.codegen(symbol_table, out_name = "R", tape = tape)
    return stitch(statements,symtab=symbol_table,tape=tape, out_name="R")



__all__ = ['chainify', 'CRnum', 'chain_ast']

