from .codegen import *
import llvmlite 
from .core import *
from .crterm import *
import sympy
import numpy, numba
from collections import namedtuple




def cr_compile(expression, environment):
    expr = sympy.parsing.sympy_parser.parse_expr(expression)
    cr = crmake(expr, sympy.Symbol('y'), 2)
    term = CRterm(cr)
    term.prepare(environment, True,2)
    return compile_cr_vec(term,llvmlite.ir.FloatType(), 2)

def cr_scalarcompile(expression, environment):
    expr = sympy.parsing.sympy_parser.parse_expr(expression)
    cr = crmake(expr)
    print(cr)
    term = CRterm(cr)
    term.prepare(environment, True)
    # return compile_cr(term, llvmlite.ir.FloatType())





# we should make a handler class for the CR that has all the symbols that we care about in it. We can reorder the class and stuff as we so choose.
# it will also be where the CRterm and CSE things reside as well.

# TWO MAIN WAYS FOR NOW:
# 1. directly compile to a function end to end. 

def chainify(expr_string, vectorized = False):
    expr_symbolic, symbol_table = parse_string(expr_string, None, vectorized)
    cr = crmake(expr_symbolic,symbol_table)
    return cr, symbol_table

def vchainify(expr_string, vector_symbol, lane_width=4):
    expr_symbolic, symbol_table = parse_string(expr_string, vectorized=True)
    cr = crmake(expr_symbolic, symbol_table)

# dont give a symbol table
def parse_string(s,symbol_table = None, vectorized = False):
    expr = sympy.parsing.sympy_parser.parse_expr(s)
    
    symbols = sympy.ordered(expr.free_symbols)
    # create auxiliary symbols representing start step
    symbol_table = {} if symbol_table is None else symbol_table
    for symbol in symbols:
        if not symbol in symbol_table:
            # symbol_table[symbol] = {'order': len(symbol_table), 'params': (0, 1)}   
            step = sympy.Symbol(f'{symbol}_h') if not vectorized else 4*sympy.Symbol(f"{symbol}_h")
            start = sympy.Symbol(f'{symbol}_0') if not vectorized else sympy.Symbol(f"{symbol}_0") + sympy.Symbol("t")
            symbol_table[symbol] = {'order': len(symbol_table), 'params': (start,step )}    
    return expr,symbol_table


    


# not needed since we don't use numba anymore
# def compile_ast(cr_ast):
#     namespace = {"numpy":numpy, "numba":numba}
#     code = compile(cr_ast, filename="<ast>", mode="exec")
#     exec(code,namespace)
#     return namespace["generated"]

def crmake(ASTnode, outermost=sympy.Symbol(''), width=0):
    if isinstance(ASTnode, sympy.Number): return CRnum(ASTnode)

    elif isinstance(ASTnode, sympy.Symbol):
        name = ASTnode.name

        if ASTnode == outermost and width > 0:
            operands = [CRnum(f"{name}_0")+CRnum("t"), CRnum(width)*CRnum(f"{name}_h")]
            res = CRsum(operands, ASTnode)
            return res
        else:
            
            operands = [CRnum(f"{name}_0"), CRnum(f"{name}_h")]
            res = CRsum(operands, ASTnode)
            return res
    
    elif isinstance(ASTnode, sympy.Add):
        arglist = ASTnode.args
        result  = crmake(arglist[0], outermost, width)
        for i in range(1,len(arglist)):
            result += crmake(arglist[i], outermost, width)
        return result
    
    elif isinstance(ASTnode, sympy.Mul):
        arglist = ASTnode.args
        result = crmake(arglist[0], outermost, width)
        for i in range(1,len(arglist)):
            result *= crmake(arglist[i], outermost, width)
        return result
    
    elif isinstance(ASTnode, sympy.Pow):
        base = crmake(ASTnode.args[0], outermost, width)
        exponent = crmake(ASTnode.args[1], outermost, width )
        return base ** exponent
    
    elif isinstance(ASTnode, sympy.exp):
        arg = crmake(ASTnode.args[0], outermost, width)
        return CRnum(sympy.E)**arg
    
    elif isinstance(ASTnode,sympy.functions.elementary.trigonometric.TrigonometricFunction):
        if isinstance(ASTnode, sympy.sin):
            arg = crmake(ASTnode.args[0], outermost, width)
            return sin(arg)
        elif isinstance(ASTnode, sympy.cos):
            arg = crmake(ASTnode.args[0], outermost, width)
            return cos(arg)
        elif isinstance(ASTnode, sympy.tan):
            arg = crmake(ASTnode.args[0], outermost, width)
            return tan(arg)
        elif isinstance(ASTnode, sympy.cot):
            arg = crmake(ASTnode.args[0], outermost, width)
            return cot(arg)
    
    elif isinstance(ASTnode, sympy.log):
        if len(ASTnode.args) == 1:
            arg = crmake(ASTnode.args[0], outermost, width)
            return log(arg)
        elif len(ASTnode.args) == 2:
            arg = crmake(ASTnode.args[0], outermost, width)
            base = crmake(ASTnode.args[1], outermost, width)
            return log(arg, base)
        


# of the form variable, start, step


# TODO: add numpy modes



__all__ = ['chainify', 'CRnum', 'chain_ast', 'compile_ast', 'generate_code']