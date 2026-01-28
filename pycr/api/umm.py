import sympy
import core


# GOAL: pull the string from the user and convert it into CR form

from sympy import simplify
from sympy.parsing.sympy_parser import parse_expr

def cr_from_string(s):
    expr = parse_expr(s)
    # we also want to simplify the expression to some degree

    free_syms = expr.free_symbols

    # foreach symbol make a start symbol S and a step symbol H
    sym_table = {}
    for sym in free_syms:
        S = sympy.Symbol(f'{sym}_0')
        H = sympy.Symbol(f'{sym}_h')
        sym_table[sym] = (S, H)
    
    # for each free symbol we create a 
    print(expr, free_syms)
    print(sym_table)