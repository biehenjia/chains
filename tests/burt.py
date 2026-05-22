import pycr, numpy, time

expr = "cos(0.3*x**3+0.5*x**2+2*x*y-0.5*y**2)"
# expr = "x**2+y**2"
environment = {"x_0":-2, "x_h":0.004, "y_0":-2,"y_h":0.004}

f = pycr.cr_compile(expr, environment)

X = 1000
A = numpy.zeros((X,X),dtype=numpy.float32)
start = time.perf_counter()
f(A,X,X)
end = time.perf_counter()

import plotly.graph_objects as go

fig = go.Figure(go.Surface(x=x, y=y, z=out, colorscale='RdBu_r'))
fig.show()