import pycr

expr = "x**2+y**2"
cr, st = pycr.chainify(expr)
print(cr)