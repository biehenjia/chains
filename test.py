from pycr.api import *
from pycr.core import *
from pycr.engine import *
from pycr.codegen import *
import ast

expr, symbol_table = parse_string("cos(x)+exp(x)")
print(symbol_table)
cr = crmake(expr, symbol_table)
print(cr)

crt = CRterm(cr)
tape = crt.prepare(symbol_table)
print(tape)

t = crt.codegen(symbol_table, out_name="R", tape=tape)

thing = stitch(t,symtab=symbol_table, tape=tape, out_name="R")
print(ast.unparse(thing))