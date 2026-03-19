import pycr, ast 
import numpy
expr = "x**2 + y**2"

a = pycr.chain_ast(expr)
# code = pycr.compile_ast(a)


def code(R, y_0, y_h, y_b, x_0, x_h, x_b):
    r0 = x_0 ** 2 + y_0 ** 2
    r1 = y_0 * y_h + y_h * (y_0 + y_h)
    r2 = 2 * y_h ** 2
    r3 = x_0 ** 2 + y_0 ** 2
    r4 = x_0 ** 2 + y_0 ** 2
    r5 = x_0 * x_h + x_h * (x_0 + x_h)
    r6 = 2 * x_h ** 2
    r7 = x_0 ** 2 + y_0 ** 2
    
    for _i0 in range(0, y_b):
        print("SHIFTING OUTER")
        print(r0,r1,r2,r3,r4,r5,r6,r7)
        r0 += r1
        r1 += r2
        r3 = r0
        print(r0,r1,r2,r3,r4,r5,r6,r7)
        r4 = r3
        input()
        for _i1 in range(0, x_b):
            print("SHIFTING INNER")
            print(r0,r1,r2,r3,r4,r5,r6,r7)
            R[_i0][_i1] = r7
            
            r4 += r5
            r5 += r6
            r7 = r4
            print(r0,r1,r2,r3,r4,r5,r6,r7)
            input()

print(ast.unparse(a))

A = numpy.zeros((10,10))
code(A,0,1,10,0,1,10)
print(A)