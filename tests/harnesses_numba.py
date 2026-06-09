import ast, time, json, datetime as dt
from pathlib import Path
import numpy as np
from numba import njit, prange  # noqa

BUDGET, TRIALS, STEPS = 10**6, 10, 200
RESULTS = Path("results.json")
FUNCS = {"sin","cos","tan","asin","acos","atan","atan2","sinh","cosh","tanh",
         "exp","log","log2","log10","sqrt","abs","floor","ceil","pi","e"}

def variables(expr):
    tree = ast.parse(expr, mode="eval")
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} - FUNCS
    return sorted(names)

def compile(expr, vars):
    sig = ", ".join(f"_{v}" for v in vars)
    unpack = "; ".join(f"{v}=_{v}[i]" for v in vars)
    src = f"""
from numba import njit, prange
from numpy import sin, cos, tan, exp, log, sqrt, pi, e
@njit(parallel=True, fastmath=True)
def k({sig}, out):
    for i in prange(out.size):
        {unpack}
        out[i] = {expr}
"""
    ns = {}; exec(src, ns); return ns["k"]

def grid(dim, n):
    ax = [np.linspace(-1, 1, n) for _ in range(dim)]
    return [a.ravel() for a in np.meshgrid(*ax, indexing="ij")] if dim > 1 else ax

def bench(expr):
    vars = variables(expr); dim = len(vars)
    k = compile(expr, vars)
    lo, hi = max(2, int(1e4 ** (1/dim))), int(BUDGET ** (1/dim))
    Ns = np.unique(np.linspace(lo, hi, STEPS).astype(int))
    g = grid(dim, lo); k(*g, np.empty(g[0].size))  # warmup
    rows = []
    for N in Ns:
        g = grid(dim, int(N)); out = np.empty(g[0].size)
        ts = []
        for _ in range(TRIALS):
            t0 = time.perf_counter(); k(*g, out); ts.append(time.perf_counter() - t0)
        mean = float(np.mean(ts))
        rows.append([int(g[0].size), mean, g[0].size / mean])
        print(f"  N={g[0].size:>8d}  {mean*1e3:8.3f} ms  {g[0].size/mean:.2e} pts/s")
    return dim, vars, rows

def run():  
    store = json.loads(RESULTS.read_text()) if RESULTS.exists() else {}
    stamp = dt.datetime.now().isoformat(timespec="seconds")
    for line in Path("expressions.txt").read_text().splitlines():
        expr = line.strip()
        if not expr or expr.startswith("#"): continue
        print(expr)
        dim, vars, rows = bench(expr)
        store.setdefault(expr, []).append(
            {"timestamp": stamp, "dim": dim, "vars": vars, "rows": rows})
    RESULTS.write_text(json.dumps(store, indent=2))

run()