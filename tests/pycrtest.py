import harnesses

exprs = [
    "x**2"
]

for expr in exprs:
    cr_scalar = []
    harnesses.test_cr_scalar(expr, 10**4, cr_scalar)
    cr_vector = []
    harnesses.test_cr_vector(expr, 10**4, cr_vector)
    cr_scalar_parallel = []
    harnesses.test_cr_scalar_parallel(expr, 10**4, cr_scalar_parallel)


def stats(records):
    print(f"min: {min(records)}")
    print(f"max: {max(records)}")
    print(f"avg: {sum(records)/len(records)}")

stats(cr_scalar)
print('---')
stats(cr_vector)
print('---')
stats(cr_scalar_parallel)

