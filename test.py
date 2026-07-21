import pycr
from pycr.crconfig import initialize_env
from pycr.analysis.subexpressions import prepare_cse, cse

expr = "sin(x*y)"
cr = pycr.parse(expr)

print(f"=== {expr} : pre-CSE ===")
print(cr)

env = initialize_env(cr)
prepare_cse(env, cr)
cr2 = cse(env, {}, cr)

print(f"\n=== {expr} : post-CSE ===")
print(cr2)
