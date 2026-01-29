import sympy

a = 0

as_thing = sympy.Integer(a)
b = sympy.Integer(as_thing)

print(b)
print(type(b))