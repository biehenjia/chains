# TODO:
- fix case for scalar evaluation 
- fix incorrect CREconnector pulling sin and cos types together
- when replacing for t in reparametrization, t should multiply the step value

- vectorized trig sequences are fine in theory; there's something amiss about my code generation. (runs fine).
- favour contiguous blocks of CR's instead of strict postorder. For example: 

Currently, for the following chain,

CRsin(y)
├─ CRsin((sin(t + x_0 + y_0), x))
|   ├─ CRnum(sin(t + x_0 + y_0))
|   ├─ CRnum(sin(x_h))
|   ├─ CRnum(cos(t + x_0 + y_0))
|   └─ CRnum(cos(x_h))
├─ CRnum(sin(2*y_h))
├─ CRcos((cos(t + x_0 + y_0), x))
|   ├─ CRnum(sin(t + x_0 + y_0))
|   ├─ CRnum(sin(x_h))
|   ├─ CRnum(cos(t + x_0 + y_0))
|   └─ CRnum(cos(x_h))
└─ CRnum(cos(2*y_h))

The inner CRsin is separated from the CRnum & CRcos. See below:
CRsin(x variable)
[0, sin(1)]
[sin(1), sin(1)]
[1, cos(1)]
[cos(1), cos(1)]

CRsin(y variable numeral)
[0, sin(1)]

[sin(2), sin(2)]

CRcos(x variable)
[0, sin(1)]
[sin(1), sin(1)]
[1, cos(1)]
[cos(1), cos(1)]

CRcos(y variable numeral)
[1, cos(1)]

[cos(2), cos(2)]

Thus, when we shift, we aren't pulling things within the same block.
Fix is to 

- Consider interpreted paradigm for code generation and discuss benefits


# chains
chains of recurrences engine in python

# installation

## pip
```bash
pip install git+https://github.com/biehenjia/chains
```

## manual
```bash
git clone https://github.com/biehenjia/chains
```

# examples
```python
from pycr import chainify

cr, symbol_table = chainify("x**2+sin(x)+4")

print(cr)
print(symbol_table)
```