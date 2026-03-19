import plotly.graph_objects as go
import numpy as np
import pycr
import ast

import inspect

def plot_surfaces(*arrays):
    fig = go.Figure()

    for z in arrays:
        z = np.array(z)
        x = np.arange(z.shape[1])
        y = np.arange(z.shape[0])

        fig.add_surface(x=x, y=y, z=z)

    fig.show()

def plot_lines(*arrays):
    fig = go.Figure()

    for y in arrays:
        y = np.array(y)
        x = np.arange(len(y))
        fig.add_scatter(x=x, y=y, mode="lines")
    fig.show()

def test(x0,xh, xb ,y0, yh, yb, f):
    x = np.arange(x0,xb, xh )
    y = np.arange(y0, yb, yh)
    return f(x[:,None], y)

def npsin(v1, v2):
    return np.pow(v1,2) + np.pow(v2,2)



expr = "x**2+y**2"
code = pycr.compile_ast(pycr.chain_ast(expr))

A = np.zeros((20,20))

mtrx = test(-10, 1, 10, -10,1,10, npsin)

code(A, -10, 1, 20, -10, 1, 10)
print(ast.unparse(pycr.chain_ast(expr)))
plot_surfaces (A)
