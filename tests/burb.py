

def f(x,y):
    r0 = 0
    r1 = 1
    r2 = 2
    r3 = 0
    r4 = 1
    r5 = 2
    res = [[0 for i in range(x)] for j in range(y) ]
    for i in range(x):
        r0 += r1
        r1 += r2
        for j in range(y):
            res[j][i] = r3
            r3 += r4
            r4 += r5
        r3 = r0
        r4 = 1
    for row in res:
        print(" ".join(list(map(str,row))))

f(10,10)
