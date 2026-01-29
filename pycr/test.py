import sympy

s = '2**x'

expr = sympy.sympify(s)

ls = sympy.ln(expr)
print(ls)