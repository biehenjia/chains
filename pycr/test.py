import api, engine, core

expr = 'sin(x)**2+cos(x)**2'
s, symbol_table = api.parse_string(expr)
cr = engine.crmake(s, symbol_table)

temp = core.CRnum(5)
temp *= cr
print(cr)
term = engine.CRterm(temp, (None, None))
tape = term.produce_tape()
print(tape)
