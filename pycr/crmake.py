from core import *
from sympy import Add, Mul, Pow, cos, sin, tan
print("loaded!")

symbolTable = {'x':[0,1]}

def crmake(expr):
    if isinstance(expr, Add):
        result = CRnum(0)
        for arg in expr.args:
            result += crmake(arg)
        return result
    elif isinstance(expr, Mul):
        result = CRnum(1)
        for arg in expr.args:
            result *= crmake(arg)
        return result
    elif isinstance(expr, Pow):
        base = crmake(expr.args[0])
        exponent = crmake(expr.args[1])
        return base ** exponent
    elif expr.is_number:
        return CRnum(expr)
    elif expr.is_symbol:
        return CRsum(symbolTable[str(expr)])
    else:
        raise ValueError(f"Unsupported expression type: {type(expr)}")
    

