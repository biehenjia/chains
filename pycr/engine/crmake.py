# here we accept sympy AST
import sympy
from ..core import *

def crmake(ASTnode, symbol_table):

    if isinstance(ASTnode, sympy.Number):
        return CRnum(ASTnode)
    
    elif isinstance(ASTnode, sympy.Symbol):
        
        entry = symbol_table[ASTnode]
        order = entry['order']
        start,step = entry['params']
        operands = (CRnum(start), CRnum(step))
        result = CRsum(operands, order)

        return result
    
    elif isinstance(ASTnode, sympy.Add):
        arglist = ASTnode.args
        result  = crmake(arglist[0],symbol_table)
        for i in range(1,len(arglist)):
            result += crmake(arglist[i], symbol_table)
        return result
    
    elif isinstance(ASTnode, sympy.Mul):
        arglist = ASTnode.args
        result = crmake(arglist[0],symbol_table)
        for i in range(1,len(arglist)):
            result *= crmake(arglist[i], symbol_table)
        return result
    
    elif isinstance(ASTnode, sympy.Pow):
        base = crmake(ASTnode.args[0], symbol_table)
        exponent = crmake(ASTnode.args[1], symbol_table)
        return base ** exponent
    
    elif isinstance(ASTnode, sympy.exp):
        arg = crmake(ASTnode.args[0], symbol_table)
        return CRnum(sympy.E)**arg
    
    elif isinstance(ASTnode,sympy.functions.elementary.trigonometric.TrigonometricFunction):
        if isinstance(ASTnode, sympy.sin):
            arg = crmake(ASTnode.args[0], symbol_table)
            return sin(arg)
        elif isinstance(ASTnode, sympy.cos):
            arg = crmake(ASTnode.args[0], symbol_table)
            return cos(arg)
        elif isinstance(ASTnode, sympy.tan):
            arg = crmake(ASTnode.args[0], symbol_table)
            return tan(arg)
        elif isinstance(ASTnode, sympy.cot):
            arg = crmake(ASTnode.args[0], symbol_table)
            return cot(arg)
    
    elif isinstance(ASTnode, sympy.log):
        if len(ASTnode.args) == 1:
            arg = crmake(ASTnode.args[0], symbol_table)
            return log(arg)
        elif len(ASTnode.args) == 2:
            arg = crmake(ASTnode.args[0], symbol_table)
            base = crmake(ASTnode.args[1], symbol_table)
            return log(arg, base)
        
