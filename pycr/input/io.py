import sympy


# TODO: error reduction

def parse_string(s,symbol_table = None, vectorized = False):
    expr = sympy.parsing.sympy_parser.parse_expr(s)
    
    symbols = sympy.ordered(expr.free_symbols)
    # create auxiliary symbols representing start step
    symbol_table = {} if symbol_table is None else symbol_table
    for symbol in symbols:
        if not symbol in symbol_table:
            # symbol_table[symbol] = {'order': len(symbol_table), 'params': (0, 1)}   
            step = sympy.Symbol(f'{symbol}_h') if not vectorized else 4*sympy.Symbol(f"{symbol}_h")
            symbol_table[symbol] = {'order': len(symbol_table), 'params': (sympy.Symbol(f'{symbol}_0'),step )}    
    return expr,symbol_table



# x is from 0 to 100, then we get
# x1 = 0 to 10, x2 = 0 to 10.
# for any iteration, we have x = x1*10 + x2