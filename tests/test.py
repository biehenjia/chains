import pycr, numpy, time

DEFAULTS = {"x_0":0, "x_h":1, "y_0":0, "y_h":1}

def test_scalar():
    s = "exp(0.25*x**2 - 0.3*x**2) * cos(x**3 + 0.5* x**2 + 2*x*y - 0.5 * y**2)"
    cr, st = pycr.parse(s)
    policy = pycr.ScalarPolicy(pycr.f32)
    res = numpy.zeros((10**3, 10**3), dtype=numpy.float32)
    f,tape = pycr.prepare_function(cr, policy=policy)
    xtape = pycr.prepare_tape(tape, {"x_0":0, "x_h":1, "y_0":0, "y_h":1})
    start = time.perf_counter()
    f(res, xtape)
    end = time.perf_counter()
    print(end - start)
    return res

def test_cre():
    s = "sin(x)+1"
    cr, st = pycr.parse(s)
    policy = pycr.ScalarPolicy(pycr.f32)
    res = numpy.zeros(10**4, dtype=numpy.float32)
    f,tape = pycr.prepare_function(cr, policy=policy)
    xtape = pycr.prepare_tape(tape, {"x_0":0, "x_h":0.1, "y_0":0, "y_h":0.1})
    start = time.perf_counter()
    f(res, xtape)
    end = time.perf_counter()
    print(end - start)
    return res

def test_vector():
    # exp(0.25*x^2-0.3*y^2)*cos(0.3*x^3+0.5*x^2+2*x*y-0.5*y^2)

    s = "exp(0.25*x**2 - 0.3*x**2) * cos(x**3 + 0.5* x**2 + 2*x*y - 0.5 * y**2)"
    cr, st = pycr.parse(s)
    # print(cr)
    policy = pycr.VectorPolicy(pycr.f32, 4)
    res = numpy.zeros((10**3, 10**3), dtype=numpy.float32)
    f, tape = pycr.prepare_function(cr, policy =policy)
    xtape = pycr.prepare_tape(tape, DEFAULTS )
    start = time.perf_counter()
    f(res,xtape)
    end = time.perf_counter()
    print(end - start)
    return res

def test_parallel():
    s = "x**2+y**2"
    cr, st = pycr.parse(s)
    print(st)
    policy = pycr.VectorPolicy(pycr.f32, 1)
    res = numpy.zeros((10,10),dtype = numpy.float32)
    f,tape = pycr.prepare_function(cr, policy= policy)
    tapes = pycr.prepare_parallel(cr, tape, (10,10), DEFAULTS, numpy.float32, 4)
    res = numpy.zeros((10,10),dtype = numpy.float32)
    pycr.dispatch_parallel(f, res,tapes, (10,10))
    print(res)
test_parallel()