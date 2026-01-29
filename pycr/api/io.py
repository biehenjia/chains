import sympy


# RIVET: the process of closing chain links in chainmail forging 
def parse_string(s,error_reduction = False):
    expr = sympy.parsing.sympy_parser.parse_expr(s)
    symbols = expr.free_symbols

    print(expr,symbols)

    if error_reduction:
        pass

    return expr,symbols


s = 'x**2 + E*sin(y*pi) + 3'

(parse_string(s))