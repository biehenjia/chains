from .cr import *

# ruleset
from .add import *
from .mul import *
from .pow import *
from .sin import *
from .cos import *
from .tan import *

__all__ = [
    'CR', 'CRnum', 'CRsum', 'CRprod', 
    'CRtrig', 'CRsin', 'CRcos', 'CRtan', 'CRcot',
    'CRE', 'CREadd', 'CREmul', 'CREpow',
    'CREtrig', 'CREsin', 'CREcos', 'CREtan', 'CREcot',

    'sin', 'cos', 'tan','cot',
]