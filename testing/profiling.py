import sys, dis, time

def callback(a):
    def decorator(f):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = f(*args, **kwargs)
            end = time.perf_counter()
            a.append(end-start)
            return result
        return wrapper
    return decorator