import pycr, ast, numba, time,numpy

expr = "x**2+y**2"
chain , st = pycr.chainify(expr)
ir = pycr.IR(chain, st)
g = pycr.Generator(ir)
code = g.generate_parallel()

print(ast.unparse(code))
f = numba.njit(pycr.compile_ast(code),parallel=True)
# ir.printape()


f(numpy.zeros((5,5)), 0,1,0,1,1,1,4)
X = Y =Z = 1000
A = numpy.zeros((X,Y))


start = time.perf_counter()
f(A,0,1,0,1,X,Y,4)
end = time.perf_counter()
print(end-start)


print(A)
# asm = list(f.inspect_asm().values())[0]

# first_fn_end = asm.find('__ZN7cpython')
# print(asm[:first_fn_end])