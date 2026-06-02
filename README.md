# TODO:
- numeric instanced CSE is not working; default to symbolic mode for trig cases


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