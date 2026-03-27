import numpy

def generated(A, R, B_0, B_1):
    r_0 = R_0 = R[0]
    r_1 = R_1 = R[1]
    r_2 = R_2 = R[2]
    r_3 = R_3 = R[3]
    r_4 = R_4 = R[4]
    r_5 = R_5 = R[5]
    r_6 = R_6 = R[6]
    r_7 = R_7 = R[7]
    for L_0 in range(B_0):
        
        r_0 += r_1
        r_1 += r_2
        r_3 = r_0
        for L_1 in range(B_1):
            print(r_0,r_1,r_2,r_3,r_4,r_5,r_6,r_7)
            A[L_0, L_1] = r_7
            r_4 += r_5
            r_5 += r_6
            r_7 = r_4

        r_4 = R_4
        r_5 = R_5
        r_6 = R_6

        r_4 = r_3
        r_7 = r_4

X = Y = 10

A = numpy.zeros((X,Y))
R = [0,1,2,0,0,1,2,0]
generated(A,R,X,Y)
print(A)