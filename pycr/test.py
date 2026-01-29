e = 'x**3 + 2*x**2+4+y+e'

from sympy import *

expr = sympify(e)
symbols = expr.free_symbols
print(symbols)