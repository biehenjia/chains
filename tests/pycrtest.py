import harnesses

exprs = [
    # "x**2",
    # "sin(x)",
    # "cos(20*x)*exp(x**2)"
    "exp(0.25*x**2 - 0.3*x**2) * cos(x**3 + 0.5* x**2 + 2*x*y - 0.5 * y**3)",
    # "exp(0.25*x**2 - 0.3*y**2) * cos(x**3 + 0.5*x**2 + 2*x*y - 0.5*y**4)  * exp(-0.1*(x**2 + y**2)) * (sin(2.1*x - 0.6*y**3 + 0.05*x**2*y**2)* cos(0.7*x*y**2 - 1.3*x**2*y + 0.4*y**3))"
    # "exp(x**3+3*x**2-3*x+1)/ 2**(x**2-2*x+1)"
]

for expr in exprs:
    cr_scalar = []
    # records, results = harnesses.test_cr_scalar(expr, 10**1, cr_scalar)
    cr_vector = []
    harnesses.test_cr_vector(expr, 10**3, cr_vector)
    cr_scalar_parallel = []
    # harnesses.test_cr_scalar_parallel(expr, 10**1, cr_scalar_parallel)
    cr_vector_parallel = []
    # harnesses.test_cr_vector_parallel(expr, 10**3,cr_vector_parallel)


def stats(records):
    print(f"min: {min(records)}")
    print(f"max: {max(records)}")
    print(f"avg: {sum(records)/len(records)}")

# stats(cr_scalar)
# print('---')
stats(cr_vector)
print('---')
# stats(cr_scalar_parallel)
# print('---')
# stats(cr_vector_parallel)
