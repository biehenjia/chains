# here we accept sympy AST
import sympy
from core import *

def crmake(ASTnode, symbolTable):

    if isinstance(ASTnode, sympy.Number):
        return CRnum(ASTnode)
    
    elif isinstance(ASTnode, sympy.Symbol):
        
        entry = symbolTable[str(ASTnode)]
        order = entry['order']
        start,step = entry['params']

        result = CRsum(order, 2)
        result[0] = CRnum(start)
        result[1] = CRnum(step)

        return result
    
    elif isinstance(ASTnode, sympy.Add):
        result = CRnum(0)
        for arg in ASTnode.args:
            result += crmake(arg, symbolTable)
        return result
    
    elif isinstance(ASTnode, sympy.Mul):
        result = CRnum(1)
        for arg in ASTnode.args:
            result *= crmake(arg, symbolTable)
        return result
    
    elif isinstance(ASTnode, sympy.Pow):
        base = crmake(ASTnode.args[0], symbolTable)
        exponent = crmake(ASTnode.args[1], symbolTable)
        return base ** exponent
    
    elif isinstance(ASTnode,sympy.functions.elementary.trigonometric.TrigonometricFunction):
        if isinstance(ASTnode, sympy.sin):
            arg = crmake(ASTnode.args[0], symbolTable)
            return sin(arg)
        elif isinstance(ASTnode, sympy.cos):
            arg = crmake(ASTnode.args[0], symbolTable)
            return cos(arg)
        elif isinstance(ASTnode, sympy.tan):
            arg = crmake(ASTnode.args[0], symbolTable)
            return tan(arg)
        elif isinstance(ASTnode, sympy.cot):
            arg = crmake(ASTnode.args[0], symbolTable)
            return cot(arg)
    
    elif isinstance(ASTnode, sympy.log):