import pycr

expr = "sin(x**2)"

chain, symbol_table = pycr.chainify(expr)


print(chain*chain+pycr.sin(chain))

ir = pycr.IR(chain,symbol_table)

G = pycr.Generator(ir)

s = G.generate()
