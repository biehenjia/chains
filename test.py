import sympy
import pycr
from pycr.core import CRnum

expr = "log(x**3+1)+(3*(x**2+x)+1)"
cr = pycr.parse(expr)

x_0, x_h = sympy.Symbol("x_0"), sympy.Symbol("x_h")
for node in cr.postorder():
    if isinstance(node, CRnum):
        node.value = sympy.S(node.value).subs({x_0: 0, x_h: 1})

print("before CSE:")
print(cr)

kernel = pycr.compile(cr)
print("\nafter CSE (as compiled):")
print(kernel.program.cr)

out = kernel(x=(0.0, 0.25, 8))
print("\nvalues at x = 0, 0.25, ..., 1.75:")
print(out)