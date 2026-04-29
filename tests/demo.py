import pycr

# expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"
expr = "log(x**3)+x**3"
chain, symbol_table = pycr.chainify(expr)

print(str(chain))
with open("field.txt","w") as f:
    f.write(str(chain))

ir = pycr.IR(chain,symbol_table)

G = pycr.Generator(ir)

s = G.generate()
