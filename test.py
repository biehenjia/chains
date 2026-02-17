import pycr
import ast
import math
import time 
expr = "sin(x**2)+2**sin(x**2)"

other, symbol_table = pycr.chainify(expr)
print(other)

stuff = pycr.chain_ast(expr)
print(ast.unparse(stuff))
f = pycr.compile_ast(stuff)
a = [0] * 10

f(a, 0,1, 10)


# issue: tower type cr, i.e., CRE class of objects
# does not have reliable eval mode when we use valueof
# e.g

# issue: update propogation, i.e., trig may need to propogate updates
# but trig does not shift itself