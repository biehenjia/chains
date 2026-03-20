from ..core import *
from .dsl import *
import sympy



def gen_shift(crterm, register_symbol = "r"):
    block = []

    if isinstance(crterm.cr, CRtrig):
        n = crterm.trunc
        t = n//2
    
    elif isinstance(crterm.cr, CRsum):
        pass

    elif isinstance(crterm.cr, CRprod):
        


