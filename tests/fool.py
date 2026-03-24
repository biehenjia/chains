import pycr, ast

expr = "x**2+y**2"
cr, symbol_table = pycr.chainify(expr)

term = pycr.CRterm(cr)
tape = term.produce_tape()
print(tape)
x = pycr.generate_code(term,symbol_table)

print(type(x))
print(ast.unparse(x))