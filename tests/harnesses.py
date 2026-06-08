import numpy, pycr, time, sympy

def test_cr_scalar(s, length, records, trials=10, dtype =numpy.float32):
    symbols = (sympy.parse_expr(s).free_symbols)
    dims = len(symbols)

    f, tape = pycr.produce_pair(s,width=1, dtype=dtype)
    mapping = {f"{v.name}_0":0 for v in symbols} | {f"{v.name}_h":1 for v in symbols}
    results = numpy.zeros(list(length for _ in range(dims)),dtype=dtype)
    tape = pycr.prepare_tape(tape, mapping)

    for i in range(trials):
        start = time.perf_counter()
        f(results,tape)
        end = time.perf_counter()
        records.append(end-start)
    return records, results


def test_cr_scalar_parallel(s, length, records, trials=10, threads=4,  dtype = numpy.float32):
    symbols = sympy.parse_expr(s).free_symbols
    lowest = min(symbols, key = str)
    dims = len(symbols)
    mapping = {f"{v.name}_0":0 for v in symbols} | {f"{v.name}_h":1 for v in symbols}

    f, tape = pycr.produce_pair(s, width=1, dtype=dtype)
    tapes = pycr.prepare_parallel(lowest,tape, list(length for i in range(dims)),mapping,dtype, threads)
    results = numpy.zeros(list(length for _ in range(dims)), dtype = dtype )

    for i in range(trials):
        start = time.perf_counter()
        pycr.dispatch_parallel(f,results, tapes, list(length for _ in range(dims)))
        end = time.perf_counter()
        records.append(end-start)
    return records, results


def test_cr_vector(s, length, records, trials=10, width = 4,dtype = numpy.float32 ):
    symbols = sympy.parse_expr(s).free_symbols
    dims = len(symbols)
    f, tape = pycr.produce_pair(s, dtype, width)
    mapping = {f"{v.name}_0":0 for v in symbols} | {f"{v.name}_h":1 for v in symbols}
    tape = pycr.prepare_tape(tape, mapping, dtype=dtype)

    results = numpy.zeros(list(length + dims - (length % dims) for _ in range(dims)), dtype = dtype )

    for i in range(trials):
        start = time.perf_counter()
        f(results, tape)
        end = time.perf_counter()
        records.append(end-start)
    slc = tuple(slice(None, length) for i in range(dims))
    return records, results[slc]


def test_cr_vector_parallel(s, length, records, trials=10, width =4, threads = 4, dtype = numpy.float32):
    symbols = sympy.parse_expr(s).free_symbols
    lowest = min(symbols, key = str)
    dims = len(symbols)
    f, tape = pycr.produce_pair(s, dtype, width)
    mapping = {f"{v.name}_0":0 for v in symbols} | {f"{v.name}_h":1 for v in symbols}
    tapes = pycr.prepare_parallel(lowest, tape, list(length for i in range(dims)), mapping)
    results = numpy.zeros(list(length + dims - (length % dims) for _ in range(dims)), dtype = dtype )
    for i in range(trials):
        start = time.perf_counter()
        pycr.dispatch_parallel(f, results, tapes, list(length + dims - (length % dims) for _ in dims), dtype = dtype)
        end = time.perf_counter()
        records.append(end - start)
    slc = tuple(slice(None, length) for i in range(dims))
    return records, results[slc ]




    

