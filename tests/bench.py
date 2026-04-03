import time

def _fmt(t):
    if t is None:
        return "N/A"
    if t >= 1:
        return f"{t:.4f}s"
    elif t >= 1e-3:
        return f"{t*1e3:.4f}ms"

def benchmark(times=None,repeats=2):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            last_result = None
            for i in range(repeats):
                start = time.perf_counter()
                fn(*args, **kwargs)
                end = time.perf_counter()
                if isinstance(times, list):
                    times.append(end-start)
            return last_result
        return wrapper
    return decorator


