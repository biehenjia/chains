import pycr


expr = "sin(x)**2+ exp(sin(x)**2)"
stuff = pycr.chain_ast(expr)
code = compile(stuff, filename="bla", mode="exec")
