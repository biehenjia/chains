import harnesses

exprs = [
    "x**2",
    "sin(x)",
    
]

for expr in exprs:
    cr_scalar = []
    records, results = harnesses.test_cr_scalar(expr, 10**8, cr_scalar)
    cr_vector = []
    harnesses.test_cr_vector(expr, 10**8, cr_vector)
    cr_scalar_parallel = []
    harnesses.test_cr_scalar_parallel(expr, 10**8, cr_scalar_parallel)
    cr_vector_parallel = []
    harnesses.test_cr_vector_parallel(expr, 10**8,cr_vector_parallel)


def stats(records):
    print(f"min: {min(records)}")
    print(f"max: {max(records)}")
    print(f"avg: {sum(records)/len(records)}")

stats(cr_scalar)
print('---')
stats(cr_vector)
print('---')
stats(cr_scalar_parallel)
print('---')
stats(cr_vector_parallel)
