import pycr

cr, symbol_table = pycr.chainify("ln(x)+(sin(x**2))+sin(2*x+1)")

print(cr)
print(symbol_table)
a = pycr.engine.crterm.CRterm(cr)
a.cse()

for s in a.postorder():
    for c in s.digests:
        print(c)
    print(s.updates)
    print('___')
