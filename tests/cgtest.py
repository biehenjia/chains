import pycr, llvmlite

expr = "x**2"

cr, _ = pycr.chainify(expr)
st = {'x_0':0, 'x_h':1, 'y_0': 0, 'y_h':1}
ncr = cr.seeded(st)



term = pycr.CRterm(ncr)
term.cr = pycr.cse({},term.cr)
print(term.cr)

f = pycr.compile_cr_vec(term, llvmlite.ir.FloatType(), W=4 )

print(f.ir_opt) 
