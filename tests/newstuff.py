import numpy, numba, time

@numba.njit(boundscheck=False, fastmath=True)
def generated(A, R, B_0, B_1):
    r = numpy.copy(R)
    UR_1 = numpy.array([3])
    UW_1 = numpy.array([4])
    for L_0 in range(B_0):
        for i in range(2):
            r[i] += r[i + 1]
        
        r[3] = r[0]
        for L_1 in range(B_1):
            A[L_0, L_1] = r[7]

            for i in range(2):
                r[4 + i] += r[4 + i + 1]
            r[7] = r[4]
            
        
        for k in range(3):
            r[4 + k] = R[4 + k]
        # for i in range(1):
        #     r[UW_1[i]] = r[UR_1[i]]
        r[4] = r[3]
        r[7] = r[4]
        


X = 1000
Y = 1000


A = numpy.zeros((X,Y))
R = numpy.array([0,1,2,0,0,1,2,0])
generated(A,R,1,1)

A = numpy.zeros((X,Y))
R = numpy.array([0,1,2,0,0,1,2,0])

start = time.perf_counter()
generated(A,R,X,Y)
end = time.perf_counter() 

print(end-start)
