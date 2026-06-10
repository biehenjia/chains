import sympy
from ..core import CRnum, CRsum, sin, cos, tan, cot, log


def crmake(node):
    if isinstance(node, sympy.Number):
        res = CRnum(node)
    elif isinstance(node, sympy.Symbol):
        start = sympy.Symbol(f"{node.name}_0")
        step = sympy.Symbol(f"{node.name}_h")
        res = CRsum([CRnum(start), CRnum(step)], node)
    elif isinstance(node, sympy.Add):
        res = crmake(node.args[0])
        for arg in node.args[1:]: res = res + crmake(arg)
    elif isinstance(node, sympy.Mul):
        res = crmake(node.args[0])
        for arg in node.args[1:]: res = res * crmake(arg)
    elif isinstance(node, sympy.Pow): res = crmake(node.args[0]) ** crmake(node.args[1])
    elif isinstance(node, sympy.exp): res = CRnum(sympy.E) ** crmake(node.args[0])
    elif isinstance(node, sympy.sin): res = sin(crmake(node.args[0]))
    elif isinstance(node, sympy.cos): res = cos(crmake(node.args[0]))
    elif isinstance(node, sympy.tan): res = tan(crmake(node.args[0]))
    elif isinstance(node, sympy.cot): res = cot(crmake(node.args[0]))
    elif isinstance(node, sympy.log):
        arg = crmake(node.args[0])
        if len(node.args) == 1: res = log(arg)
        else: res = log(arg, crmake(node.args[1]))
    return res
