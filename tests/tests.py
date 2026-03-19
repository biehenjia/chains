import json
import time
import math
import numpy as np
from numba import njit
import pycr
import sympy
import flame

with open("equations.json") as f:
    cfg = json.load(f)

repeats = cfg.get("repeats", 5)
expressions = cfg["expressions"]

xs = np.arange(1000, dtype=np.float64)
ys = np.arange(1000, dtype=np.float64)
x_flat = np.repeat(xs, 1000)
y_flat = np.tile(ys, 1000)


def make_python(expr):
    env = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "exp": math.exp,
        "log": math.log,
        "sqrt": math.sqrt,
        "abs": abs,
    }
    return eval(f"lambda x, y: {expr}", env)


def make_numpy(expr):
    env = {
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "sqrt": np.sqrt,
        "abs": np.abs,
    }
    return eval(f"lambda x, y: {expr}", env)


def make_numba(expr):
    src = f"""
def f(x_arr, y_arr, out):
    for i in range(x_arr.shape[0]):
        x = x_arr[i]
        y = y_arr[i]
        out[i] = {expr}
    return out
"""
    ns = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "exp": math.exp,
        "log": math.log,
        "sqrt": math.sqrt,
        "abs": abs,
    }
    exec(src, ns)
    return njit(ns["f"])

def make_crJIT(expr):
    code = pycr.compile_ast(pycr.chain_ast(expr))
    return njit(code)

def make_cr(expr):
    code = pycr.compile_ast(pycr.chain_ast(expr))
    return code


def bench(fn, repeats):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return min(times), sum(times) / len(times)


def benchmark_expression(expr):
    py_f = make_python(expr)
    np_f = make_numpy(expr)
    nb_f = make_numba(expr)
    cr_f = make_cr(expr)
    crnjit_f = make_crJIT(expr)


    def run_python():
        out = np.empty_like(x_flat)
        for i in range(x_flat.shape[0]):
            out[i] = py_f(float(x_flat[i]), float(y_flat[i]))
        return out

    def run_numpy():
        return np_f(x_flat, y_flat)

    def run_numba():
        out = np.empty_like(x_flat)
        return nb_f(x_flat, y_flat, out)
    
    def run_cr():
        out = np.zeros((xs.shape[0],ys.shape[0]))
        cr_f(out,0,1,xs.shape[0], 0,1, ys.shape[0])

    def run_crjit():
        out = np.zeros((xs.shape[0],ys.shape[0]))
        crnjit_f(out, 0,1, xs.shape[0], 0,1, ys.shape[0])
        return out


    run_numba()
    out = run_crjit()
    flame.plot_surfaces(out)

    py_min, py_avg = bench(run_python, repeats)
    np_min, np_avg = bench(run_numpy, repeats)
    nb_min, nb_avg = bench(run_numba, repeats)
    cr_min, cr_avg = bench(run_cr, repeats)
    crjit_min, crjit_avg = bench(run_crjit, repeats)
    return {
        "expr": expr,
        "python_min": py_min,
        "python_avg": py_avg,
        "numpy_min": np_min,
        "numpy_avg": np_avg,
        "numba_min": nb_min,
        "numba_avg": nb_avg,
        "cr_min": cr_min,
        "cr_avg": cr_avg,
        "crjit_min": crjit_min,
        "crjit_avg": crjit_avg
    }


results = [benchmark_expression(expr) for expr in expressions]

print(f"{'expr':40} {'python':>12} {'numpy':>12} {'numba':>12} {'cr':>12} {"crjit":>12}")
print("-" * 96)
for r in results:
    print(
        f"{r['expr'][:40]:40} "
        f"{r['python_avg']:12.6f} "
        f"{r['numpy_avg']:12.6f} "
        f"{r['numba_avg']:12.6f}"
        f"{r['cr_avg']:12.6f}"
        f"{r['crjit_avg']:12.6f}"
        
    )