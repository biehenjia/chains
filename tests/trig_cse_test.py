import pycr

expr = "exp(0.25*x**2-0.3*y**2)*cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"

cr, st = pycr.chainify(expr)

with open("dump.txt","w") as f:
    f.write(str(cr))

cse_cr = pycr.cse({},cr)

with open("dump2.txt",'w') as f:
    f.write(str(cse_cr))
    