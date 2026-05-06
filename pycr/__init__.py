from .input import *
from .codegen import *
from .core import *
from .engine import * 
import sympy
import numpy, numba

def chainify(expr_string):
    expr_symbolic, symbol_table = parse_string(expr_string)
    cr = crmake(expr_symbolic,symbol_table)
    return cr, symbol_table

def vchainify(expr_string, vector_symbol, lane_width=4):
    expr_symbolic, symbol_table = parse_string(expr_string)

def compile_ast(cr_ast):
    namespace = {"numpy":numpy, "numba":numba}
    code = compile(cr_ast, filename="<ast>", mode="exec")
    exec(code,namespace)
    return namespace["generated"]

# of the form variable, start, step


# TODO: add numpy modes



__all__ = ['chainify', 'CRnum', 'chain_ast', 'compile_ast', 'generate_code']