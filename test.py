import pycr

expr = "sin(x)*exp(x)"

cr = pycr.api.parse(expr)
print(cr)
