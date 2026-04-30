import pycr

# expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"

expr1 = "x*x"
chain1, symbol_table = pycr.chainify(expr1)
print(chain1)
table = {
    'x_0': 0,
    'x_h' : 1
}

chain2 = chain1.seeded(table)
print(chain2)

expr2 = "2*x+1"
bla, symbol_table = pycr.chainify(expr2)
bla1 = bla.seeded(table)
print(bla1)
sh1 = bla1._suffixhash()
chainhashes = chain2._suffixhash()

for a in sh1:
    for b in chainhashes:
        print(a== b)

# ir = pycr.IR(chain,symbol_table)
# G = pycr.Generator(ir)
# s = G.generate()
