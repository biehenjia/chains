import pycr, numpy, time


def run_scalar():
    s = "x**2+y**2"
    cr, st = pycr.parse(s)
    print(cr)
    f, tape = pycr.generate_scalar(cr)
    print(tape)
    res = numpy.zeros((5, 5 ), dtype=numpy.float32)
    print(res.shape, res.dtype, id(res))
    f(res, tape)
    for row in res:
        print(row)

def test_scalar():
    s = "x**2+y**2"
    cr, st = pycr.parse(s)
    policy = pycr.ScalarPolicy(pycr.f32)
    res = numpy.zeros((10**3, 10**3), dtype=numpy.float32)
    f,tape = pycr.prepare_function(cr, policy=policy)
    xtape = pycr.prepare_tape(tape, {"x_0":1, "x_1":1, "y_0":0, "y_h":1})
    start = time.perf_counter()
    f(res, xtape)
    end = time.perf_counter()
    print(end-start)
    
    



def run_vectorized():
    s = "x**2+y**2"
    cr, st = pycr.parse(s)

    
    t1 = numpy.array([0,1,4,9],dtype = numpy.float32)
    t2 = numpy.array([16,24,32,40], dtype= numpy.float32)
    t3 = numpy.array([32,32,32,32],dtype = numpy.float32)
    tape = numpy.array([t1,t2,t3], dtype = numpy.float32)

    f = pycr.test_vector(cr)
    res = numpy.zeros(10, dtype= numpy.float32)
    f(res,tape)
    print(res)

test_scalar()