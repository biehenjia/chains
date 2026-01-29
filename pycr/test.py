import api, engine

def test():
    expr = "3+log(x)+y"
    ast, symbol_table = api.parse_string(expr)
    cr_tree = engine.crmake(ast, symbol_table)
    print(cr_tree)

test()