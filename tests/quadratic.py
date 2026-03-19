import numpy

res = numpy.zeros((10,10),dtype=int)




x = [0,1,2]
y = [0,1,2]
yb = [0,1,2]

for i in range(10):
    for xi in range(len(x)-1):
        x[xi] += x[xi+1]
    
    for j in range(10):
        print(f"{y=}")
        #input()
        res[i][j] = y[0]
        for yi in range(len(y)-1):
            y[yi] += y[yi+1]
        
    y = yb[::]
    y[0] = x[0]
        

print(res)        