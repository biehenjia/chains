import sympy
from .crmake import crmake

def parse(expr_string):
    expr = sympy.parsing.sympy_parser.parse_expr(expr_string)
    free = sorted(expr.free_symbols, key=lambda s: s.name)
    symbol_table = {s: (sympy.Symbol(f"{s.name}_0"), sympy.Symbol(f"{s.name}_h")) for s in free}
    cr = crmake(expr, symbol_table)
    return cr, symbol_table

