from numpy import *
from numba import *

def generated(A, x_0, x_h, y_0, y_h, B_0, B_1):
    r_0 = R_0 = x_0 ** 2
    r_1 = R_1 = x_0 * x_h + x_h * (x_0 + x_h)
    r_2 = R_2 = 2 * x_h ** 2
    r_3 = R_3 = x_0 ** 2
    r_4 = R_4 = sin(y_0)
    r_5 = R_5 = sin(y_h)
    r_6 = R_6 = cos(y_0)
    r_7 = R_7 = cos(y_h)
    r_8 = R_8 = sin(y_0)
    r_9 = R_9 = x_0 ** 2
    r_10 = R_10 = sin(y_0)
    r_11 = R_11 = x_0 ** 2 + sin(y_0)
    for L_0 in range(B_0):
        r_0 += r_1
        r_1 += r_2
        r_3 = r_0
        for L_1 in range(B_1):
            A[L_0, L_1] = r_11
            __a = r_4 * r_7 + r_6 * r_5
            __b = r_6 * r_7 - r_6 * r_5
            r_4 = __a
            r_6 = __b
            r_8 = r_4
            r_11 = r_9 + r_10
        r_4 = R_4
        r_5 = R_5
        r_6 = R_6
        r_7 = R_7
        r_8 = r_4
        r_9 = R_9
        r_10 = R_10
        r_9 = r_3
        r_10 = r_8
        r_11 = r_9 + r_10

A = zeros((10,10))

generated(A,0.0,1.0,0.0,1.0,10,10)
print(A)