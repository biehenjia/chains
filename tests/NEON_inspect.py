import numba, numpy

V1 = numpy.array([0,1,4,9])
V2 = numpy.array([1,3,5,7])
V3 = numpy.array([2,2,2,2])


@numba.njit
def test(V1,V2,V3,R,BOUND):
    for i in range(BOUND):
        V1 += V2
        V2 += V3
        R[i:i+4] = V1

X = 4 * 10**4
R = numpy.zeros(X)
test(V1,V2,V3,R,X)
        
    
