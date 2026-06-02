from .cr import *

# ruleset
from .add import *
from .mul import *
from .pow import *
from .sin import *
from .cos import *
from .tan import *
from .log import * 

__all__ = [
    'CR', 'CRnum', 'CRsum', 'CRprod', 
    'CRtrig', 'CRsin', 'CRcos', 'CRtan', 'CRcot',
    'CRE', 'CREadd', 'CREmul', 'CREpow', 'CRElog',
     'CREsin', 'CREcos', 'CREtan', 'CREcot', 'CREconnector',

    'sin', 'cos', 'tan','cot', 'log'
]

op1 = CRnum(sympy.Symbol('x_0'))
op2 = CRnum(sympy.Symbol('x_h'))
x = CRsum([op1,op2],sympy.Symbol('x'))
x.expr = sympy.Symbol('x')

x2 = x*x
print(x2)