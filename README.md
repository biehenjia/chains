# installation

```
pip install git+https://github.com/biehenjia/chains
```

# dependencies

```
1. numpy
2. sympy
3. llvmlite
```

# getting started

constructing a function from a string
```python
import pycr
import numpy

fn = pycr.compile("x**2", dtype = numpy.float32, width = 4, threads = 4)
bound = fn.bind(x=(0,1,100))
bound()
out = bound.result
```
constructing a function from a CR


```python
import pycr
import numpy

cr = pycr.parse("x")
cr2 = cr ** 2 + 2 * cr 

fn = pycr.compile(cr2, dtype = numpy.float32)
bound = fn.bind(x=(0,1,100))
bound()
out = bound.result
```