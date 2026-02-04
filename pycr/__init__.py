from .api import *
from .codegen import *
from .core import *
from .engine import * 

def chainify(expr_string):
    expr_symbolic, symbol_table = parse_string(expr_string)
    cr = crmake(expr_symbolic,symbol_table)
    return cr, symbol_table



__all__ = ['chainify']