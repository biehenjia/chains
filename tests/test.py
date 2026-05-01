import testcase, numpy
from bench import benchmark
import json
m = {}

with open("equations.txt","r") as f:

    for l in f.readlines():
        tc = testcase.Testcase(l)
        # for i in range(6):
        n = 10**4
        A = numpy.zeros((n,n),dtype=numpy.float32)
        funcs, results = tc.getall(n,r=5)

        for method in funcs:
            thing = funcs[method]
            thing(A)
        m[l] = results
        print(f"done {l}")

with open("r.txt","w") as f:
    f.write(json.dumps(m,indent=4))