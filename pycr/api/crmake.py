from ..core import *
import sympy

def crmake(node, symbol_table):
    if isinstance(node, sympy.Number): res = CRnum(node)
    elif isinstance(node, sympy.Symbol):
        start, step = symbol_table[node]
        res = CRsum([CRnum(start), CRnum(step)], node)
        # res.expr = node
    elif isinstance(node, sympy.Add):
        res = crmake(node.args[0], symbol_table)
        for arg in node.args[1:]: res = res + crmake(arg, symbol_table)
    elif isinstance(node, sympy.Mul):
        res = crmake(node.args[0], symbol_table)
        for arg in node.args[1:]: res = res * crmake(arg, symbol_table)
    elif isinstance(node, sympy.Pow): res = crmake(node.args[0], symbol_table) ** crmake(node.args[1], symbol_table)
    elif isinstance(node, sympy.exp): res = CRnum(sympy.E) ** crmake(node.args[0], symbol_table)
    elif isinstance(node, sympy.sin): res = sin(crmake(node.args[0], symbol_table))
    elif isinstance(node, sympy.cos): res = cos(crmake(node.args[0], symbol_table))
    elif isinstance(node, sympy.tan): res = tan(crmake(node.args[0], symbol_table))
    elif isinstance(node, sympy.cot): res = cot(crmake(node.args[0], symbol_table))
    elif isinstance(node, sympy.log):
        arg = crmake(node.args[0], symbol_table)
        if len(node.args) == 1: res = log(arg)
        else: res = log(arg, crmake(node.args[1], symbol_table))
    return res
