import sympy
from .crmake import crmake

def parse(expr_string: str):
    expr = sympy.parsing.sympy_parser.parse_expr(expr_string)
    return crmake(expr)
