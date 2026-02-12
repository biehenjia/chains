import sympy

sympy.parsing 

# TODO: error reduction

def parse_string(s,symbol_table = {}, error_reduction = 0):
    expr = sympy.parsing.sympy_parser.parse_expr(s)
    if error_reduction:
        # we break x into roughly error_reduction pieces
        transition = {}
        symbols = expr.free_symbols
        # for each symbol, 
        pass
    
    symbols = expr.free_symbols
    # create auxiliary symbols representing start step
    for symbol in symbols:
        if not symbol in symbol_table:
            # symbol_table[symbol] = {'order': len(symbol_table), 'params': (0, 1)}    
            symbol_table[symbol] = {'order': len(symbol_table), 'params': (sympy.Symbol(f'{symbol}_0'), sympy.Symbol(f'{symbol}_h'))}    
    return expr,symbol_table






# x is from 0 to 100, then we get
# x1 = 0 to 10, x2 = 0 to 10.
# for any iteration, we have x = x1*10 + x2