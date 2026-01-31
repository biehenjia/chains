import api, engine, core

expr = 'exp(2*x+1)+2*x+1'
s, symbol_table = api.parse_string(expr)
cr = engine.crmake(s, symbol_table)
print(cr)
temp = core.CRnum(5)
temp *= cr
term = engine.CRterm(temp, (None, None))
tape = term.produce_tape()
print(tape)

term.cse()

