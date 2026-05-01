import pycr
expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"
# expr = "sin(x**2+y**2+x*y)"
chain, st = pycr.chainify(expr)
print(chain)