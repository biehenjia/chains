import engine, core, codegen, api

def test_cr(expr_str, symbol_table):
    expr, symbol_table = api.parse_string(expr_str)
    cr = engine.crmake(expr, symbol_table)

    crterm = engine.CRterm(cr, symbol_table)
    buckets = crterm.partition_order(1)
    tape = crterm.produce_tape()
    code = codegen.generate_code([10], buckets, register_symbol='r')
    f = codegen.build([], code)
    return cr, code

expr = "x**2+3*x"
cr, code = test_cr(expr, {})
