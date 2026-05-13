import pycr

expr = "x**2+y**2"

cr, _ = pycr.chainify(expr)
st = {'x_0':0, 'x_h':1, 'y_0': 0, 'y_h':1}
ncr = cr.seeded(st)
print(ncr)


term = pycr.CRterm(ncr)

f = pycr.codegen.compile_cr(term)

print(f.ir_opt) 
