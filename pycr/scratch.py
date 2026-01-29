import sympy

s = 'pi/2 + pi'

expr = sympy.sympify(s)
print(sympy.sin(expr))