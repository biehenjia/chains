import gc
import math
import time
from dataclasses import dataclass, field
from functools import wraps

_ns = time.perf_counter_ns


def _percentile(data, p):
    if not data:
        raise ValueError("empty sample")
    n = len(data)
    idx = (p / 100) * (n - 1)
    lo = int(idx)
    hi = lo + 1
    frac = idx - lo
    if hi >= n:
        return float(data[lo])
    return data[lo] + frac * (data[hi] - data[lo])


def _fmt_ns(ns):
    if ns < 1_000:
        return f"{ns:.1f} ns"
    if ns < 1_000_000:
        return f"{ns/1_000:.2f} µs"
    if ns < 1_000_000_000:
        return f"{ns/1_000_000:.3f} ms"
    return f"{ns/1_000_000_000:.4f} s"


def _fmt_ops(ops):
    if ops >= 1e9:
        return f"{ops/1e9:.3f} Gop/s"
    if ops >= 1e6:
        return f"{ops/1e6:.3f} Mop/s"
    if ops >= 1e3:
        return f"{ops/1e3:.3f} Kop/s"
    return f"{ops:.1f} op/s"


def _repr_args(args, kwargs):
    parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
    s = ", ".join(parts)
    return f"args: {s}" if s else ""


@dataclass
class BenchResult:
    name: str
    iterations: int
    samples_ns: list
    jit_ns: object = None
    args_repr: str = ""
    _min_ns: float = field(init=False, repr=False)
    _median_ns: float = field(init=False, repr=False)
    _p95_ns: float = field(init=False, repr=False)
    _p99_ns: float = field(init=False, repr=False)
    _max_ns: float = field(init=False, repr=False)
    _throughput: float = field(init=False, repr=False)

    def __post_init__(self):
        s = self.samples_ns
        self._min_ns = float(s[0])
        self._max_ns = float(s[-1])
        self._median_ns = _percentile(s, 50)
        self._p95_ns = _percentile(s, 95)
        self._p99_ns = _percentile(s, 99)
        self._throughput = 1e9 / self._median_ns if self._median_ns > 0 else math.inf

    @property
    def min_ns(self): return self._min_ns

    @property
    def median_ns(self): return self._median_ns

    @property
    def p95_ns(self): return self._p95_ns

    @property
    def p99_ns(self): return self._p99_ns

    @property
    def max_ns(self): return self._max_ns

    @property
    def throughput(self): return self._throughput

    def report(self, width=60):
        bar = "─" * width
        lines = [
            f"  hotbench · {self.name}",
            f"  {self.args_repr}" if self.args_repr else "",
            bar,
            f"  iterations : {self.iterations:,}",
            f"  throughput : {_fmt_ops(self._throughput)}",
            bar,
            f"  min        : {_fmt_ns(self._min_ns)}",
            f"  median     : {_fmt_ns(self._median_ns)}",
            f"  p95        : {_fmt_ns(self._p95_ns)}",
            f"  p99        : {_fmt_ns(self._p99_ns)}",
            f"  max        : {_fmt_ns(self._max_ns)}",
        ]
        if self.jit_ns is not None:
            lines += [bar, f"  jit cost   : {_fmt_ns(self.jit_ns)}  (excluded from stats)"]
        lines.append(bar)
        return "\n".join(l for l in lines if l != "")

    def __repr__(self):
        return (f"BenchResult({self.name!r}, n={self.iterations}, "
                f"median={_fmt_ns(self._median_ns)}, throughput={_fmt_ops(self._throughput)})")


def _run_timed_loop(fn, args, kwargs, iterations, numba_warmup):
    jit_ns = None
    if numba_warmup:
        t0 = _ns()
        fn(*args, **kwargs)
        jit_ns = _ns() - t0

    gc_was_enabled = gc.isenabled()
    gc.disable()
    samples = []
    try:
        for _ in range(iterations):
            t0 = _ns()
            fn(*args, **kwargs)
            samples.append(_ns() - t0)
    finally:
        if gc_was_enabled:
            gc.enable()
        gc.collect()

    samples.sort()
    return samples, jit_ns


def bench(*, name=None, iterations=1_000, numba_warmup=False, args=(), kwargs=None, print_report=True):
    kw = kwargs or {}

    def decorator(fn):
        bench_name = name or fn.__qualname__

        @wraps(fn)
        def wrapper(*call_args, **call_kwargs):
            run_args = args if args else call_args
            run_kwargs = kw if kw else call_kwargs
            samples, jit_ns = _run_timed_loop(fn, run_args, run_kwargs, iterations, numba_warmup)
            result = BenchResult(
                name=bench_name,
                iterations=iterations,
                samples_ns=samples,
                jit_ns=jit_ns,
                args_repr=_repr_args(run_args, run_kwargs),
            )
            if print_report:
                print(result.report())
            return result

        wrapper.__wrapped__ = fn
        return wrapper

    return decorator


class LoopBench:
    def __init__(self, name="loop", *, iterations=1_000, numba_warmup_fn=None, print_report=True):
        self.name = name
        self.iterations = iterations
        self._warmup_fn = numba_warmup_fn
        self._print = print_report
        self._samples = []
        self._jit_ns = None
        self.result = None

    def __enter__(self):
        if self._warmup_fn is not None:
            t0 = _ns()
            self._warmup_fn()
            self._jit_ns = _ns() - t0
        return self

    def __iter__(self):
        gc_was_enabled = gc.isenabled()
        gc.disable()
        try:
            for _ in range(self.iterations):
                t0 = _ns()
                yield
                self._samples.append(_ns() - t0)
        finally:
            if gc_was_enabled:
                gc.enable()
            gc.collect()

    def __exit__(self, *_):
        self.result = BenchResult(
            name=self.name,
            iterations=self.iterations,
            samples_ns=sorted(self._samples),
            jit_ns=self._jit_ns,
        )
        if self._print:
            print(self.result.report())


def loop_bench(name="loop", *, iterations=1_000, numba_warmup_fn=None, print_report=True):
    return LoopBench(name, iterations=iterations, numba_warmup_fn=numba_warmup_fn, print_report=print_report)


def compare(*results, width=60):
    if not results:
        return ""
    bar = "─" * width
    baseline = results[0].throughput
    lines = [bar, f"  {'name':<28} {'throughput':>12}  {'vs baseline':>12}", bar]
    for r in results:
        ratio = r.throughput / baseline if baseline > 0 else math.inf
        ratio_str = f"{ratio:.2f}×" if r is not results[0] else "baseline"
        lines.append(f"  {r.name:<28} {_fmt_ops(r.throughput):>12}  {ratio_str:>12}")
    lines.append(bar)
    out = "\n".join(lines)
    print(out)
    return out