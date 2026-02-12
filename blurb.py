def generated(R, x_0, x_h, x_b):
    r0 = x_0 ** 2 + 2 * x_0 + 1
    r1 = x_0 * x_h + x_h * (x_0 + x_h) + 2 * x_h
    r2 = 2 * x_h ** 2
    r3 = 0
    for _i0 in range(0, x_b):
        r0 += r1
        r1 += r2
        r3 = r0
        R[_i0] = r3

R = [0] * 10

generated(R, 0,1,10)
print(R)