import pycr, ast, numba, time,numpy

expr = "x**2+y**2"
chain , st = pycr.chainify(expr)
ir = pycr.IR(chain, st)
g = pycr.Generator(ir)
code = g.generate_parallel()

print(ast.unparse(code))
# f = numba.njit(pycr.compile_ast(code))
# ir.printape()

# R = numpy.array([0,1,2,0,0,1,2,0])
# f(numpy.zeros((5,5)), R, 1,1)
# X = Y =Z = 1000
# A = numpy.zeros((X,Y))


# start = time.perf_counter()
# f(A,R,X,Y)
# end = time.perf_counter()
# print(end-start)



# asm = list(f.inspect_asm().values())[0]

# first_fn_end = asm.find('__ZN7cpython')
# print(asm[:first_fn_end])